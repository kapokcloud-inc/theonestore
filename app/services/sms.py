# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from sys import version_info
import json
import os
import uuid
from datetime import (
    date, 
    datetime, 
    timedelta
)
from app.helpers import (
    log_info,
    log_error,
    urlencode
)

from flask import current_app
from flask_babel import gettext as _
from flask_uploads import extension

from app.helpers import log_error, log_debug
from app.models.sys import SysSetting
from app.exception import ConfigNotExistException

from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

class SmsService(object):
    """ 发送短信实例 """

    def __init__(self):
        """ 初始化 """
        self.today = date.today().isoformat()
        self.sms_vendor_key = 'sms_vendor'
        self.sms_vendor = ''
        self.yunpian = {}
        self.alisms = {}

    def load_config(self):
        """ 加载配置 """
        if self.sms_vendor:
            return
        
        ss = None
        try:
            ss = self.get_config(self.sms_vendor_key)
        except ConfigNotExistException as e:
            raise e

        if ss.value not in ('sms_yunpian', 'sms_alisms'):
            raise ConfigNotExistException(_(u'短信选项只能是云片或者阿里云SMS'))
        self.sms_vendor = ss.value

        if self.sms_vendor == 'sms_yunpian':
            try:
                yunpian_config = self.get_config('config_sms_yunpian')
                self.yunpian = json.loads(yunpian_config.value)
            except (ConfigNotExistException, ValueError) as e:
                raise e
        elif self.sms_vendor == 'sms_alisms':
            try:
                alisms_config = self.get_config('config_sms_alisms')
                self.alisms = json.loads(alisms_config.value)
            except (ConfigNotExistException, ValueError) as e:
                raise e
    
    def get_config(self, key):
        """获取配置选项"""
        ss = SysSetting.query.filter(SysSetting.key == key).first()
        if ss is None:
            raise ConfigNotExistException(_(u'配置选项不存在'))

        if not ss.value:
            raise ConfigNotExistException(_(u'配置选项值为空'))
        return ss
    
    def get_service(self):
        try:
            self.load_config()
        except (ConfigNotExistException, ValueError) as e:
            raise e
        
        service = None
        if self.sms_vendor == 'sms_yunpian' and self.yunpian:
            service = YunpianSmsService(self.yunpian)
        if self.sms_vendor == 'sms_alisms' and self.alisms:
            service = AliyunSmsService(self.alisms)
        return service

    def send_sms_code(self, mobile, code):
        """ 发送短息验证码
            @parmas mobile 电话号码
            @params code 验证码
        """
        current_service = self.get_service()

        if current_service == None:
            return False

        return current_service.send_sms_code(mobile, code)
    
    def send_tpl_sms(self, mobile, tpl_id, tpl_params):
        """ 发送模版短信 
            @parmas mobile 电话号码
            @params tpl_id 模版id
            @params params 模版内容
        """
        current_service = self.get_service()

        if current_service == None:
            return False
        
        return current_service.send_tpl_sms(mobile, tpl_id, tpl_params)

    def send_mutil_sms(self, params):
        """ 批量发短信
            params必须包含  mobile 、text  两个key
        """
        current_service = self.get_service()

        if current_service == None:
            return False
        
        return current_service.send_mutil_sms(params)

class YunpianSmsService(object):
    """ 云片短信服务 """
    def __init__(self, params):
        self.api_key = params['ak']
        self.sms_prefix = params['app_name']
    
    def check_before(self):
        """ 发送前检测 """
        if not self.api_key:
            self.api_key = ''
            log_error(_(u'云片服务api_key为空'))
            return False
    
    def get_result(self, result=None):
        """ 发送反馈 """
        if not result:
            return False
            
        result_info = u'code:%s，msg:%s，data:%s，prefix:%s' % (str(result.code()), result.msg(), (result.data() if result.data() else u'[]'), self.sms_prefix)

        if result.code() != 0 :
            log_error(result_info)
            return False
        log_info(result_info)
        return True

    def send_sms_code(self, mobile='', code=''):
        """ 发送验证码 """
        if not self.check_before:
            return False
        
        if not mobile or not code:
            log_error(_(u'参数错误'))
            return False

        clnt = YunpianClient(self.api_key)
        param = {YC.MOBILE: mobile, YC.TEXT: u'%s您的验证码是%s' % ((u'' if self.sms_prefix == u'' else u'【' + self.sms_prefix + u'】'), code)}
        
        r = clnt.sms().single_send(param)
        return self.get_result(r)
        
    
    def send_tpl_sms(self, mobile='', tpl_id=0, tpl_params=None):
        """ 指定模版，单发短信 """
        if not self.check_before:
            return False

        if not mobile or not tpl_id or not tpl_params:
            log_error(_(u'参数错误'))
            return False

        clnt = YunpianClient(self.api_key)
        param = {YC.MOBILE: mobile, YC.TPL_ID: tpl_id, YC.TPL_VALUE: urlencode(tpl_params)}
        r = clnt.sms().tpl_single_send(param)
        return self.get_result(r)

    def send_mutil_sms(self, params):
        """ 群发短信 """
        if not self.check_before:
            return False

        mobile = params.get('mobile', '')
        text = params.get('text', '')
        if not mobile or not text:
            log_error(_(u'参数错误'))
            return False
        
        if len(mobile.split(',')) > 1000 or len(text.split(',')) > 1000:
            log_error(_(u'单次最多批量发送1000条'))
            return False

        if len(mobile.split(',')) !=  len(text.split(',')):
            log_error(_(u'手机号数与内容条数不相等'))
            return False
        
        param = {YC.MOBILE: mobile, YC.TEXT: text}

        clnt = YunpianClient(self.api_key)
        r = clnt.sms().multi_send(param)
        return self.get_result(r)


class AliyunSmsService(object):
    """ 阿里云短信服务 """

    def __init__(self, params):
        log_info(params)
        self.access_key_id= params['access_key_id']
        self.access_secret= params['access_key_secret']
        self.app_name = params['app_name']

    def send_sms_code(self):
        log_info('执行发阿里云短信了')
        log_info('尚未支持')
        return False