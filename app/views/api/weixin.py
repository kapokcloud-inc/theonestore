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
    request,
    redirect,
    url_for,
    session
)
from flask_babel import gettext as _

from app.database import db

from app.services.api.weixin import WeiXinLoginService

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp


weixin = Blueprint('api.weixin', __name__)

@weixin.route('/login')
def login():
    """微信登陆"""

    url  = url_for('mobile.index.root')

    wxls = WeiXinLoginService('mp', 'mp', request)
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

    wxls = WeiXinLoginService('open', 'qrcode', request)
    if not wxls.check():
        return redirect(url)

    if not wxls.check_state():
        return redirect(wxls.code_url)

    if wxls.login():
        url = session.get('weixin_login_url', url)

        session.pop('weixin_login_url', None)
        session.pop('weixin_login_state', None)

    return redirect(url)
