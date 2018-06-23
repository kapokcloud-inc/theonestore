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
from urllib import urlencode

from flask import (
    request,
    session
)

from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import set_user_session

from app.services.api.user import UserCreateService

from app.models.user import User, UserThirdBind


class WeiXinLoginService(object):
    """微信登录Service"""

    def __init__(self):
        self.msg          = u''
        self.appid        = ''
        self.secret       = ''
        self.current_time = current_timestamp()

    def check(self):
        """检查"""

        # ??
        self.appid        = ''
        self.secret       = ''

        return True

    def code_url(self):
        """code url"""

        weixin_authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        params               = {'redirect_uri':request.url.encode('utf8')}
        redirect_uri_param   = urlencode(params)
        code_url             = u'%s?appid=%s&%s&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect' % (
                                weixin_authorize_url, self.appid, redirect_uri_param)

        return code_url

    def token_url(self, code):
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

    def userinfo_url(self, access_token, openid):
        """userinfo url"""

        userinfo_url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" %\
            (access_token, openid)

        return userinfo_url

    def login(self, code):
        """登陆"""

        # 获取token
        token_url = self.token_url(code)
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
        userinfo_url = self.userinfo_url(access_token, openid)
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
                    filter(UserThirdBind.third_user_id == openid).first()
        if not utb:
            ucs = UserCreateService(user_data, self.current_time)
            if not ucs.check():
                return False

            ucs.create()
            ucs.commit()
            user = ucs.user

            utb_data = {'uid':user.uid, 'third_type':1, 'third_user_id':openid, 'third_unionid':unionid,
                        'third_res_text':json.loads(data), 'add_time':self.current_time}
            utb      = UserThirdBind(**utb_data)
            db.session.add(utb)
        else:
            user = User.query.get(utb.uid)
            if not user:
                return False

        utb.update_time = self.current_time
        db.session.commit()

        set_user_session(user)

        return True
