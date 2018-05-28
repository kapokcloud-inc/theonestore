# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from hashlib import sha256

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _

from app.helpers import (
    render_template, 
    log_info,
    toint
)
from app.database import db
from app.models.auth import AdminUsers
from app.services.admin.auth import AuthLoginService

auth = Blueprint('admin.auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登陆"""
    if request.method == 'GET':
        return render_template('admin/auth/login.html.j2', f={}, errmsg={})

    form = request.form
    mobile = form.get('mobile', '')
    password = form.get('password', '')
    als = AuthLoginService()
    ret = als.login(mobile, password)
    if not ret:
        return render_template('admin/auth/login.html.j2', f=form, errmsg=als.username)

    # 登录成功
    als.write_session(session)

    # 跳转到目标url
    return_url = request.args.get('return_url', '/admin/dashboard/')
    return redirect(return_url)


@auth.route('/create')
def create():
    """创建管理员"""
    return render_template('admin/auth/admin_user_detail.html.j2')


@auth.route('/edit/<int:admin_uid>')
def edit(admin_uid):
    """编辑管理员"""
    au = AdminUsers.query.get_or_404(admin_uid)
    return render_template('admin/auth/admin_user_detail.html.j2', au=au)


@auth.route('/delete/<int:admin_uid>')
def delete(admin_uid):
    """删除管理员"""
    au = AdminUsers.query.get_or_404(admin_uid)
    db.session.delete(au)
    db.session.commit()
    return redirect(url_for('admin.auth.index'))


@auth.route('/save', methods=['POST'])
def save():
    """保存管理员"""
    form = request.form
    admin_uid = toint(form.get('admin_uid', '0'))
    username = form.get('username', '')
    mobile = form.get('mobile', '')
    password = form.get('password', '')


    return 'save'
