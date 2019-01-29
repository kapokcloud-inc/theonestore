# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import os
import uuid
from datetime import (
    date, 
    datetime, 
    timedelta
)

from flask import current_app
from flask_babel import gettext as _
from flask_uploads import extension

from app.helpers import log_error, log_debug
from app.models.sys import SysSetting
from app.exception import ConfigNotFoundException

import qiniu
import oss2

class FileUploadService(object):
    """文件上传service"""

    def __init__(self):
        """初始化"""
        self.today = date.today().isoformat()
        self.storage_vendor_key = 'storage_vendor'
        self.storage_vendor = ''
        self.qiniu = {}
        self.alioss = {}

        # 云oss存储的key
        self.key = ''

        # 存储目标文件
        self.target_filename = ''

        self.auth = None
        self.bucket_name = ''


    def _load_config(self):
        """加载配置"""
        if self.storage_vendor:
            return

        ss = None
        try:
            ss = self._get_config(self.storage_vendor_key)
        except ConfigNotFoundException as e:
            raise e

        if ss.value not in ('qiniu', 'aliyunoss'):
            raise ConfigNotFoundException(_(u'存储选项只能是七牛云或者阿里云OSS'))

        self.storage_vendor = ss.value
        if self.storage_vendor == 'qiniu':
            try:
                qiniu_config = self._get_config('config_storage_qiniu')
                self.qiniu = json.loads(qiniu_config.value)
            except (ConfigNotFoundException, ValueError) as e:
                raise e
        elif self.storage_vendor == 'aliyunoss':
            try:
                alioss_config = self._get_config('config_storage_alioss')
                self.alioss = json.loads(alioss_config.value)
            except (ConfigNotFoundException, ValueError) as e:
                raise e


    def _get_config(self, key):
        """获取配置选项"""
        ss = SysSetting.query.filter(SysSetting.key == key).first()
        log_debug(ss)
        if ss is None:
            raise ConfigNotFoundException(_(u'配置选项不存在'))

        if not ss.value:
            raise ConfigNotFoundException(_(u'配置选项值为空'))

        return ss


    def save_storage(self, storage, category='default', filetype='image'):
        """保存文件
        :param storage: 文件对象
            :class:`~werkzeug.datastructures.FileStorage` object.
        :param category: 分类名称
        :param filetype: 文件类型
        """
        files_dest = current_app.config['UPLOADED_FILES_DEST']
        dirname = os.path.join(files_dest, category, self.today)

        # 创建目录
        try:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        except OSError as e:
            log_error(u'[OSError] [FileUploadService.save_storage] exception:%s' % e)
            raise e

        # 保存文件到硬盘
        filename_ext = extension(storage.filename).lower()
        uuid_hex = uuid.uuid4().hex
        filename = '%s.%s' % (uuid_hex, filename_ext)
        self.target_filename = os.path.join(dirname, filename)
        try:
            storage.save(self.target_filename)
        except Exception as e:
            raise e

        # 云oss存储的key
        self.key = '%s/%s/%s' % (category, self.today, filename)
        url = ''
        try:
            url = self._upload_oss()
        except Exception as e:
            log_debug(e)
            raise e

        return url


    def _upload_oss(self):
        """上传至云存储"""
        try:
            self._load_config()
        except (ConfigNotFoundException, ValueError) as e:
            raise e

        if self.storage_vendor == 'qiniu':
            return self._qiniu()
        elif self.storage_vendor == 'aliyunoss':
            return self._aliyunoss()

        return ''


    def _qiniu(self):
        """七牛存储"""
        if self.auth is None:
            access_key = self.qiniu.get('access_key', '')
            secret_key = self.qiniu.get('secret_key', '')
            self.auth = qiniu.Auth(access_key, secret_key)
            self.bucket_name = self.qiniu.get('bucket_name', '')
        
        token = self.auth.upload_token(self.bucket_name)
        ret, info = None, None
        try:
            ret, info = qiniu.put_file(token, key=self.key, file_path=self.target_filename)
        except Exception as e:
            raise e

        if info.status_code != 200:
            log_error('[QiniuNetworkError] [FileUploadService] info.status_code:%d' % info.status_code)
            raise Exception(u'网络错误')

        return ('//%s/%s' % (self.qiniu.get('cname', ''), self.key))

    
    def _aliyunoss(self):
        """阿里云存储"""
        if self.auth is None:
            access_key_id = self.alioss.get('access_key_id', '')
            access_key_secret = self.alioss.get('access_key_secret', '')
            endpoint = self.alioss.get('endpoint', '')
            self.bucket_name = self.alioss.get('bucket_name', '')
            self.auth = oss2.Auth(access_key_id, access_key_secret)
        
        bucket = oss2.Bucket(self.auth, endpoint, self.bucket_name)
        res = None
        try:
            res = bucket.put_object_from_file(self.key, 
                        self.target_filename, headers=self._headers())
        except Exception as e:
            raise e

        if res.status/100 != 2:
            log_error('[AliyunOSSNetworkError] [FileUploadService] res.status:%d' % res.status)
            raise Exception(u'网络错误')

        return ('//%s/%s' % (self.alioss.get('cname', ''), self.key))
        

    def _headers(self):
        """设置oss文件过期时间"""
        meta = {}

        expire = datetime.now() + timedelta(days=365*3)

        # HTTP/1.0 (3 years)
        meta['Expires'] = '%s GMT+0800' % expire.strftime('%a %b %d %Y %H:%M:%S')

        # HTTP/1.1 (3 years)
        expire_sec = 3*365*24*60*60
        meta['Cache-Control'] = 'max-age=%d' % expire_sec
        return meta


        
