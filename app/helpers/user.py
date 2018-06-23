# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import arrow
import time

from flask import (
    request,
    session,
    redirect,
    url_for
)

from app.helpers import (
    log_info,
    toint
)


def check_login():
    """检查登录"""

    uid = toint(session.get('uid', '0'))
    if uid == 0:
        session['weixin_login_url'] = request.headers['Referer']
        redirect(url_for('api.wx.login'))


def set_user_session(user):
    """设置用户session"""
    
    session['uid']      = user.uid
    session['nickname'] = user.nickname
    session['avatar']   = user.avatar
