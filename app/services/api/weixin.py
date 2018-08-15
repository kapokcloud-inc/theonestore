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
    toint,
    randomstr,
    model_create,
    model_update
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import set_user_session

from app.services.api.user import (
    UserCreateService,
    UserStaticMethodsService
)

from app.models.sys import SysSetting
from app.models.user import User, UserThirdBind


class WeiXinLoginService(object):
    """微信登录Service"""

    def __init__(self, config_type, login_type, request):
        self.msg          = u''
        self.appid        = ''
        self.secret       = ''
        self.config_type  = config_type         # 配置类型: mp或open
        self.login_type   = login_type          # 登录类型: mp或qrcode
        self.request      = request
        self.current_time = current_timestamp()
        self.config_types = {'mp':'config_weixin_mp', 'open':'config_weixin_open'}
        self.code_url     = ''

    def __code_url(self):
        """code url"""

        uris   = {'mp':'https://open.weixin.qq.com/connect/oauth2/authorize',
                    'qrcode':'https://open.weixin.qq.com/connect/qrconnect'}
        scopes = {'mp':'snsapi_userinfo', 'qrcode':'snsapi_login'}

        uri = uris.get(self.login_type)
        params = OrderedDict()
        params['appid'] = self.appid
        params['redirect_uri'] = request.url
        params['response_type'] = 'code'
        params['scope'] = scopes.get(self.login_type)
        params['state'] = randomstr(32)
        query_string = urlencode(params)
        self.code_url = u'%s?%s#wechat_redirect' % (uri, query_string)

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

    def check(self):
        """检查"""

        if self.config_type not in ['mp', 'open']:
            self.msg = _(u'参数错误')
            return False

        if self.login_type not in ['mp', 'qrcode']:
            self.msg = _(u'参数错误')
            return False

        config_key = self.config_types.get(self.config_type)
        ss         = SysSetting.query.filter(SysSetting.key == config_key).first()
        if not ss:
            self.msg = _(u'配置错误')
            return False

        try:
            config = json.loads(ss.value)
        except Exception as e:
            self.msg = _(u'配置错误')
            return False

        self.appid  = config.get('appid', '')
        self.secret = config.get('secret', '')
        if (not self.appid) or (not self.secret):
            self.msg = _(u'配置错误')
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

        code  = self.request.args.get('code', '')
        state = self.request.args.get('state', '')

        if session.get('weixin_login_state') != state:
            return False

        # 获取token
        token_url = self.__token_url(code)
        response  = requests.get(token_url)
        if response.status_code != 200:
            return False

        data    = response.json()
        errcode = data.get('errcode', 0)
        if errcode > 0:
            return False

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
        userinfo_url = self.__userinfo_url(access_token, openid)
        response     = requests.get(userinfo_url)
        if response.status_code != 200:
            return False

        data    = response.json()
        errcode = data.get('errcode', 0)
        if errcode > 0:
            return False

        openid    = data.get('openid')
        unionid   = data.get('unionid')
        user_data = {}
        key1_key2 = {'nickname':'nickname', 'avatar':'headimgurl', 'gender':'sex',
                        'country':'country', 'province':'province', 'city':'city'}
        for key1, key2 in key1_key2.items():
            user_data[key1] = data.get(key2, '')

        # 绑定登录
        utb = UserThirdBind.query.\
                    filter(UserThirdBind.third_type == 1).\
                    filter(UserThirdBind.third_unionid == unionid).first()
        if not utb:
            ucs = UserCreateService(user_data, self.current_time)
            if not ucs.check():
                return False

            # 创建用户
            ucs.create()
            ucs.commit()
            user = ucs.user

            # 创建帐户
            UserStaticMethodsService.create_account(user.uid, self.current_time, is_commit=False)

            # 创建绑定
            data = {'uid':user.uid, 'third_type':1,
                    'third_user_id':openid, 'third_unionid':unionid,
                    'third_res_text':json.dumps(data), 'add_time':self.current_time}
            utb  = model_create(UserThirdBind, data)
        else:
            user = User.query.get(utb.uid)
            if not user:
                return False

        model_update(utb, {'update_time':self.current_time}, commit=True)

        set_user_session(user)

        return True
