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

    code = request.args.get('code', '')
    wxs  = WeiXinLoginService()

    if not code:
        return redirect(wxs.code_url())

    index_url = url_for('mobile.index.root')

    if not wxs.check():
        return redirect(index_url)

    url = index_url
    if wxs.login(code):
        url = session.get('weixin_login_url', '')
        url = url if url else index_url

        session.pop('weixin_login_url', None)

    return redirect(url)
