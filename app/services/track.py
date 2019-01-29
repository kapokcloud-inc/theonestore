# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import time
import requests
from hashlib import sha256, md5
from app.helpers import (
    log_info,
    toint
)
from app.models.sys import SysSetting
from app.exception import (
    ConfigNotFoundException,
    ParamNotFoundException,
    TheonestoreException,
    NetworkException
)

class TrackService(object):
    """ 物流查询 """
    def __init__(self, shipping_code, shipping_sn):
        self.msg           = u'' #信息
        self.shipping_code = shipping_code #快递编码
        self.shipping_sn   = shipping_sn #快递单号
        self._shipping_url  = ''  #快递查询地址
    
    #物流查询
    def track(self):
        pass

class Shipping100TrackService(TrackService):
    """ 快递100物流查询 """

    def __init__(self, shipping_code='', shipping_sn='', params=None):

        TrackService.__init__(self, shipping_code, shipping_sn)
        self._customer     = u''
        self._key          = u''
        self._shipping_url = 'https://poll.kuaidi100.com/poll/query.do'
        self.params       = params # 附加参数 phone(收寄手机号) from(出发地，广东深圳) to(目的地，北京朝阳)

    def track(self):
        """ 查询 """

        try:
            self.__obtain_config() #获取参数
            extra_params = self.__check() #检查参数
            
            # 查询
            post_data = {'com':self.shipping_code, 'num':self.shipping_sn}
            post_data.update(extra_params)
            
            # 拼接字符串后MD5加密,字符串转大写
            json_params = json.dumps(post_data)
            temp_sign = u'%s%s%s' % (json_params, self._key, self._customer)
            sign = md5(temp_sign.encode('utf8')).hexdigest()
            sign = sign.upper()
            
            #请求接口
            data = {'customer':self._customer, 'param':json_params, 'sign':sign}
            res  = requests.post(self._shipping_url, data=data)
            res.encoding = 'utf8'

            if res.status_code != 200:
                raise NetworkException(u'查询失败')
            
            data = res.json()
            if data['message'] != 'ok':
                raise NetworkException(u'查询失败')
        except (TheonestoreException, Exception) as e:
            self.msg = e.__str__()
            log_info(self.msg)
            return (self.msg, [])
        else:
            return (u'ok', data['data'])

    def __check(self):
        """ 检查 """

        if not self.shipping_code:
            raise ParamNotFoundException(u'缺少快递公司编码')

        if not self.shipping_sn:
            raise ParamNotFoundException(u'缺少快递单号')
        
        # 非必要参数
        extra_params = {}
        if self.params and type(self.params).__name__ == 'dict':
            for key in self.params.keys():
                if key not in ['phone', 'from', 'to']:
                   return extra_params
                else:
                    extra_params[key] = self.params[key]
        else:
            return extra_params

    def __obtain_config(self):
        """ 获取配置 """
    
        shipping = SysSetting.query.filter(SysSetting.key == 'config_shipping').first()
        try:
            if not shipping or not shipping.value:
                raise ConfigNotFoundException(u'配置不存在')
        
            data = json.loads(shipping.value)
            self._customer = data.get('customer', '')
            self._key = data.get('key', '')
            if self._customer == '' or self._key == '':
                raise ConfigNotFoundException(u'配置值不存在')
        except ConfigNotFoundException as e:
            raise e
