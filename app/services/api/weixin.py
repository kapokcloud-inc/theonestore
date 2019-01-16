# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from collections import OrderedDict
import json
import requests
try:
    from urllib.parse import urlencode
except ImportError as identifier:
    from urllib import urlencode

from flask import (
    request,
    session
)

from flask_babel import gettext as _

from app.helpers import (
    log_info,
    randomstr,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import get_uid

from app.services.api.bind import BindService
from app.services.api.cart import CartStaticMethodsService

from app.models.sys import SysSetting


class WeiXinLoginService(object):
    """微信登录Service"""

    def __init__(self, login_type):
        self.msg          = u''
        self.appid        = ''
        self.secret       = ''
        self.login_type   = login_type          # 登录类型: mp或qrcode或xiao
        self.request      = request
        self.current_time = current_timestamp()
        self.config_types = {'mp':'config_weixin_mp', 'qrcode':'config_weixin_open', 'xiao':'config_weixin_xiao'}
        self.third_types  = {'mp':1, 'qrcode':2, 'xiao':3}
        self.code_url     = ''

    def __code_url(self):
        """code url"""

        uris   = {'mp':'https://open.weixin.qq.com/connect/oauth2/authorize', 'qrcode':'https://open.weixin.qq.com/connect/qrconnect'}
        scopes = {'mp':'snsapi_userinfo', 'qrcode':'snsapi_login'}

        uri                     = uris.get(self.login_type)
        params                  = OrderedDict()
        params['appid']         = self.appid
        params['redirect_uri']  = self.request.url
        params['response_type'] = 'code'
        params['scope']         = scopes.get(self.login_type)
        params['state']         = randomstr(32)
        query_string            = urlencode(params)
        self.code_url           = u'%s?%s#wechat_redirect' % (uri, query_string)

        session['weixin_login_state'] = params['state']
        return True

    def __token_url(self, code):
        """token url"""

        access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params           = {
                                'appid':self.appid.encode('utf8'),
                                'secret':self.secret.encode('utf8') ,
                                'code':code.encode('utf8'),
                                'grant_type':'authorization_code'.encode('utf8'),
                            }
        token_url        = u'%s?%s' % (access_token_url, urlencode(params))

        return token_url

    def __userinfo_url(self, access_token, openid):
        """userinfo url"""

        userinfo_url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" %\
            (access_token, openid)

        return userinfo_url

    def __connect_mp_open(self):
        """连接公众平台或开放平台"""

        false = (False, '', '', {}, {})
        code  = self.request.args.get('code', '')
        state = self.request.args.get('state', '')

        if session.get('weixin_login_state') != state:
            return false

        # 获取token
        token_url = self.__token_url(code)
        response  = requests.get(token_url)
        if response.status_code != 200:
            return false

        data    = response.json()
        errcode = data.get('errcode', 0)
        if errcode > 0:
            return false

        openid        = data.get('openid')
        access_token  = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in    = data.get('expires_in')

        session['weixin_login_openid']        = openid
        session['weixin_login_access_token']  = access_token
        session['weixin_login_refresh_token'] = refresh_token
        session['weixin_login_expires_in']    = expires_in
        session['weixin_login_token_time']    = self.current_time

        # 获取用户信息
        userinfo_url      = self.__userinfo_url(access_token, openid)
        response          = requests.get(userinfo_url)
        response.encoding = 'utf8'
        if response.status_code != 200:
            return false

        data    = response.json()
        errcode = data.get('errcode', 0)
        if errcode > 0:
            return false

        openid    = data.get('openid')
        unionid   = data.get('unionid')
        user_data = {}
        key1_key2 = {'nickname':'nickname', 'avatar':'headimgurl', 'gender':'sex',
                        'country':'country', 'province':'province', 'city':'city'}
        for key1, key2 in key1_key2.items():
            user_data[key1] = data.get(key2, '')

        return (True, openid, unionid, data, user_data)

    def __connect_xiao(self):
        """连接小程序"""

        false    = (False, '', '', {}, {})
        jscode   = self.request.args.get('jscode', '')
        nickname = self.request.args.get('nickname', '')
        avatar   = self.request.args.get('avatar', '')
        gender   = toint(self.request.args.get('gender', 0))

        if not jscode:
            self.msg = _(u'缺少jscode')
            return false

        if not nickname or not avatar:
            self.msg = _(u'缺少用户信息')
            return false

        user_data = {'nickname':nickname, 'avatar':avatar, 'gender':gender, 'country':'', 'province':'', 'city':''}

        uri                  = 'https://api.weixin.qq.com/sns/jscode2session'
        params               = OrderedDict()
        params['appid']      = self.appid
        params['secret']     = self.secret
        params['js_code']    = jscode
        params['grant_type'] = 'authorization_code'
        query_string         = urlencode(params)
        url                  = u'%s?%s' % (uri, query_string)

        response  = requests.get(url)
        if response.status_code != 200:
            self.msg = _(u'连接请求错误')
            return false

        data    = response.json()
        errcode = data.get('errcode', 0)
        if errcode > 0:
            self.msg = _(u'登录请求错误')
            return false

        openid      = data.get('openid')
        session_key = data.get('session_key')
        unionid     = data.get('unionid')

        return (True, openid, unionid, data, user_data)

    def __connect(self):
        """连接第三方"""

        if self.login_type in ['mp', 'qrcode']:
            data = self.__connect_mp_open()
        else:
            data = self.__connect_xiao()

        return data

    def check(self):
        """检查"""

        if self.login_type not in ['mp', 'qrcode', 'xiao']:
            self.msg = _(u'参数错误')
            return False

        config_key = self.config_types.get(self.login_type)
        ss         = SysSetting.query.filter(SysSetting.key == config_key).first()
        if not ss:
            self.msg = ('配置错误1:' +  config_key)
            return False

        try:
            config = json.loads(ss.value)
        except Exception as e:
            self.msg = _(u'配置错误2')
            return False

        self.appid  = config.get('appid', '')
        self.secret = config.get('secret', '')
        if (not self.appid) or (not self.secret):
            self.msg = _(u'配置错误3')
            return False

        return True

    def check_state(self):
        """检查state"""

        state = self.request.args.get('state', '')
        if not state:
            self.__code_url()
            return False

        return True

    def login(self):
        """登陆"""

        # 绑定类型
        third_type = self.third_types.get(self.login_type)

        # 连接第三方
        ret, openid, unionid, res_text, user_data = self.__connect()
        if not ret:
            return False

        # 绑定登录
        bs = BindService(third_type, openid, unionid, res_text, user_data, self.current_time)
        if not bs.bind():
            return False

        # 登陆后迁移购物车商品项
        uid        = get_uid()
        session_id = session.sid
        CartStaticMethodsService.move(uid, session_id)

        return True
