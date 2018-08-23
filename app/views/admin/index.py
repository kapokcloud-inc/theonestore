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

@index.route('/')
def root():
    """管理后台首页"""
    admin_uid = session['admin_uid']
    if admin_uid:
        return redirect(url_for('index.dashboard'))

    return_url = request.args.get('return_url', '/admin/dashboard')
    return redirect(url_for('admin.auth.login', return_url=return_url))


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
    return redirect('admin/auth/login')
    