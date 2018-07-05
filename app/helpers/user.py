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

    return False if uid == 0 else True


def set_user_session(user):
    """设置用户session"""
    
    session['uid']      = user.uid
    session['nickname'] = user.nickname
    session['avatar']   = user.avatar


def get_uid():
    """获取用户ID"""

    return toint(session.get('uid', 0))


def get_nickname():
    """获取用户昵称"""

    return session.get('nickname', '')


def get_avatar():
    """获取用户头像"""

    return session.get('avatar', '')


def get_session_id():
    """获取用户session_id"""

    return session.get('session_id', '')
