# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import requests
try:
    from urllib.parse import urlencode
except ImportError as identifier:
    from urllib import urlencode

from flask_babel import gettext as _

from app.helpers import (
    log_info,
    log_error,
    toint,
    model_create,
    model_update
)
from app.helpers.date_time import current_timestamp

from app.models.sys import (
    SysSetting,
    SysToken
)
from app.models.user import UserThirdBind
from app.models.weixin import WeixinMpTemplate


class WeiXinMpAccessTokenService(object):
    """微信公众平台AccessTokenService"""

    def __init__(self):
        self.appid        = ''
        self.secret       = ''
        self.current_time = current_timestamp()
        self.st           = None

    def __check(self):
        """检查"""

        ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_mp').first()
        if not ss:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config is none.')
            return False

        try:
            config = json.loads(ss.value)
        except Exception as e:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config data error.')
            return False

        self.appid  = config.get('appid', '')
        self.secret = config.get('secret', '')
        if (not self.appid) or (not self.secret):
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config is empty.')
            return False

        return True

    def __request_token(self):
        """获取token"""

        token = ''

        if not self.__check():
            return token

        
        params   = {'grant_type':'client_credential',
                    'appid':self.appid.encode('utf8'),
                    'secret':self.secret.encode('utf8')}
        url      = 'https://api.weixin.qq.com/cgi-bin/token'
        url      = u'%s?%s' % (url, urlencode(params))
        response = requests.get(url)
        if response.status_code != 200:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceRequestToken][RequestError]  request error.')
            return token

        data    = response.json()
        errcode = data.get('errcode', 0)
        errmsg  = data.get('errmsg', '')
        if errcode > 0:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceRequestToken][RequestError]  errcode:%s  errmsg:%s' %\
                (errcode, errmsg))
            return token

        token      = data.get('access_token', '')
        expires_in = data.get('expires_in', 0)

        if not self.st:
            self.st = model_create(SysToken, {'token_type':'weixin_mp', 'add_time':self.current_time})

        expires_in = self.current_time + expires_in - 60
        model_update(self.st, {'access_token':token, 'expires_in':expires_in}, commit=True)

        return token

    def get_token(self):
        """获取token"""
        token   = ''
        expires = 0

        self.st = SysToken.query.filter(SysToken.token_type == 'weixin_mp').first()
        if self.st:
            token   = self.st.token
            expires = self.st.expires_in

        if (token == '') or (self.current_time > expires):
            token = self.__request_token()

        return token


class WeiXinMpMessageService(object):
    """微信公众平台模板消息Service"""

    def __init__(self, uid, wmt_id, data, url=''):
        self.uid          = uid
        self.wmt_id       = wmt_id
        self.data         = data
        self.url          = url
        self.current_time = current_timestamp()
        self.openid       = ''
        self.access_token = ''
        self.template_id  = ''

    def __check(self):
        """检查"""

        utb = UserThirdBind.query.filter(UserThirdBind.uid == self.uid).first()
        if not utb or utb.third_user_id == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][UserError]  no openid.')
            return False
        self.openid = utb.third_user_id

        wmats             = WeiXinMpAccessTokenService()
        self.access_token = wmats.get_token()
        if self.access_token == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][AccessTokenError]  no token.')
            return False

        wmt = WeixinMpTemplate.query.get(self.wmt_id)
        if not wmt or wmt.template_id == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][TemplateError]  no template.')
            return False
        self.template_id = wmt.template_id

        return True

    def push(self):
        """推送"""
        if not self.__check():
            return False

        url  = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % self.access_token
        data = {'touser':self.openid, 'template_id':self.template_id, 'data':self.data, 'url':self.url}
        data = json.dumps(data)
        response = requests.post(url, data=data)
        if response.status_code != 200:
            log_error('[ErrorServiceWeixinWeiXinMpMessageServicePush][RequestError]  request error.')
            return False

        data    = response.json()
        errcode = data.get('errcode', 0)
        errmsg  = data.get('errmsg', '')
        if errcode > 0:
            log_error('[ErrorServiceWeixinWeiXinMpMessageServicePush][RequestError]  errcode:%s  errmsg:%s' %\
                (errcode, errmsg))
            return False

        return True


class WeixinMessageStaticMethodsService(object):

    @staticmethod
    def create_order(uid, order_sn, pay_amount):
        """推送创建订单消息"""

        url  = ''
        data = {'first':_(u'您的订单已创建，请尽快完成支付。'),
                'keyword1':order_sn, 'keyword2':pay_amount,
                'remark':_(u'请点击详情在线付款。')}

        wxmms = WeiXinMpMessageService(uid, 1, data, url)
        wxmms.push()

        return True
