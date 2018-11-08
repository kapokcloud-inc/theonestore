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
from app.helpers import (
    log_info,
    log_error
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
        current_service = self.get_service()

        if current_service == None:
            return False

        return current_service.send_sms_code(mobile, code)

class YunpianSmsService(object):
    """ 云片短信服务 """
    def __init__(self, params):
        self.api_key = params['ak']
        self.sms_prefix = params['app_name']

    def send_sms_code(self, mobile, code):
        if not self.api_key:
            self.api_key = ''
            raise ConfigNotExistException(_(u'云片服务api_key为空'))

        clnt = YunpianClient(self.api_key)
        param = {YC.MOBILE: mobile,YC.TEXT:'%s您的验证码是%s' % (('' if self.sms_prefix == '' else '【' + self.sms_prefix + '】'), code)}
        r = clnt.sms().single_send(param)
        result_info = 'code:%s，msg:%s，data:%s，prefix:%s' % (str(r.code()), r.msg(), (r.data() if r.data() else '[]'), self.sms_prefix)
        if r.code() != 0 :
            log_error(result_info)
            return False
        log_info(result_info)
        return True

class AliyunSmsService(object):
    """ 阿里云短信服务 """

    def __init__(self, params):
        log_info(params)
        self.access_key_id= params['access_key_id']
        self.access_secret= params['access_key_secret']
        self.app_name = params['app_name']

    def send_sms_code(self):
        log_info('执行发阿里云短信了')
        pass