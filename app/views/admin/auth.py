# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import time
from hashlib import sha256

from werkzeug.datastructures import CombinedMultiDict
from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for,
    g
)
from flask_babel import gettext as _
from wtforms.compat import with_metaclass, iteritems, itervalues

from app.helpers import (
    render_template, 
    log_info,
    log_error,
    toint,
    randomstr
)
from app.database import db
from app.forms.admin.auth import AdminUsersForm
from app.models.auth import AdminUsers
from app.services.admin.auth import AuthLoginService
from app.services.uploads import FileUploadService

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


@auth.route('/')
def index():
    """管理员列表"""
    g.page_title = _(u'管理员')

    admin_users = AdminUsers.query.all()
    return render_template('admin/auth/admin_user_index.html.j2', admin_users=admin_users)

@auth.route('/create')
def create():
    """创建管理员"""
    g.page_title = _(u'添加管理员')

    form = AdminUsersForm()
    return render_template('admin/auth/admin_user_detail.html.j2', form=form)


@auth.route('/edit/<int:admin_uid>')
def edit(admin_uid):
    """编辑管理员"""
    g.page_title = _(u'编辑管理员')
    au = AdminUsers.query.get_or_404(admin_uid)

    form = AdminUsersForm()
    form.fill_form(au)
    return render_template('admin/auth/admin_user_detail.html.j2', form=form)


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
    form = AdminUsersForm(CombinedMultiDict((request.files, request.form)))
    if not form.validate_on_submit():
        return render_template('admin/auth/admin_user_detail.html.j2', form=form)
    
    admin_uid = toint(form.admin_uid.data)
    au = AdminUsers()
    if admin_uid > 0:
        au = AdminUsers.query.filter(AdminUsers.admin_uid == admin_uid).first()
    else:
        db.session.add(au)
        au.add_time = int(time.time())
        au.salt = randomstr(random_len=32)
        password = sha256(form.password.data.encode('utf8')).hexdigest()
        sha256_password_salt = sha256((password+au.salt).encode('utf8')).hexdigest()
        au.password = sha256(sha256_password_salt.encode('utf8')).hexdigest()

    fus = FileUploadService()
    try:
        avatar = fus.save_storage(form.avatar.data, 'avatar')
    except Exception as e:
        log_error(u'[FileUploadService] Exception:%s' % e)
        form.avatar.errors = (_(u'上传失败，请检查云存储配置'),)
        return render_template('admin/auth/admin_user_detail.html.j2', form=form)

    au.username = form.username.data
    au.mobile = form.mobile.data
    au.nickname = form.username.data
    au.update_time = int(time.time())
    au.avatar = avatar
    db.session.commit()

    return redirect(url_for('admin.auth.index'))

