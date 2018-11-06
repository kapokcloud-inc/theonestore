# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import (
    Blueprint,
    redirect,
    url_for,
    session
)
from flask_babel import gettext as _

from app.database import db
from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.services.response import ResponseJson
from app.services.api.weixin import WeiXinLoginService
from app.services.weixin import WeiXinMpAccessTokenService

weixin = Blueprint('api.weixin', __name__)

resjson = ResponseJson()
resjson.module_code = 19

@weixin.route('/login')
def login():
    """微信登陆"""

    url  = url_for('mobile.index.root')

    wxls = WeiXinLoginService('mp')
    if not wxls.check():
        return redirect(url)

    if not wxls.check_state():
        return redirect(wxls.code_url)

    if wxls.login():
        url = session.get('weixin_login_url', url)

        session.pop('weixin_login_url', None)
        session.pop('weixin_login_state', None)

    return redirect(url)


@weixin.route('/login-qrcode')
def login_qrcode():
    """微信扫码登陆"""

    url  = url_for('pc.index.root')

    wxls = WeiXinLoginService('qrcode')
    if not wxls.check():
        return redirect(url)

    if not wxls.check_state():
        return redirect(wxls.code_url)

    if wxls.login():
        url = session.get('weixin_login_url', url)

        session.pop('weixin_login_url', None)
        session.pop('weixin_login_state', None)

    return redirect(url)


@weixin.route('/ticket')
def ticket():
    """微信分享ticket"""
    resjson.action_code = 10
    service = WeiXinMpAccessTokenService()
    try:
        ticket = service.get_weixin_mp_ticket()
    except Exception as e:
        return resjson.print_json(11, u'%s'%e)
    
    return resjson.print_json(0, 'ok', {'ticket':ticket})


@weixin.route('/login-xiao')
def login_xiao():
    """微信小程序登陆"""
    resjson.action_code = 10

    wxls = WeiXinLoginService('xiao')
    if not wxls.check():
        return resjson.print_json(10, _(u'登陆失败'))

    if not wxls.login():
        return resjson.print_json(11, _(u'登陆失败'))

    return resjson.print_json(0, u'ok')
