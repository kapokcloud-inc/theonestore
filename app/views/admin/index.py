# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask import (
    request,
    session,
    make_response,
    Blueprint,
    g,
    redirect,
    url_for
)

from app.helpers import render_template


index = Blueprint('admin.index', __name__)


@index.route('/dashboard')
def dashboard():
    """dashboard页"""
    return render_template('admin/dashboard/index.html.j2')
    

@index.route('/success')
def success():
    """操作成功反馈页面"""
    return render_template('admin/success.html.j2')


@index.route('/signout')
def signout():
    """退出登录"""
    session.clear()
    return redirect('/admin/auth/login')