# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import (
    request,
    session,
    make_response,
    Blueprint,
    g,
    redirect,
)

from app.helpers import render_template, log_info
from app.models.auth import AdminUsers

auth = Blueprint('admin.auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登陆"""

    if request.method == 'GET':
        args     = request.args
        mobile   = args.get('mobile', '')
        password = args.get('password', '')

        return render_template('admin/auth/login.html.j2', f={}, errormsg={})

    form     = request.form
    mobile   = form.get('mobile', '')
    password = form.get('password', '')

    if mobile and password:
        return False

    return render_template('admin/auth/login.html.j2', f={}, errormsg={})


@auth.route('/')
def index():
    """管理员列表"""
    admin_users = AdminUsers.query.all()
    return render_template('admin/auth/admin_user_index.html.j2', admin_users=admin_users)

@auth.route('/create')
def create():
    """创建管理员"""
    return render_template('admin/auth/admin_user_detail.html.j2')


@auth.route('/edit/<int:admin_uid>')
def edit(admin_uid):
    """编辑管理员"""
    return render_template('admin/auth/admin_user_detail.html.j2')


@auth.route('/delete/<int:admin_uid>')
def delete(admin_uid):
    """删除管理员"""
    return 'delete admin'


@auth.route('/save', methods=['POST'])
def save():
    """保存管理员"""
    return 'save'
