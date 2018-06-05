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
    url_for,
    g
)
from flask_babel import gettext as _
from wtforms.compat import with_metaclass, iteritems, itervalues

from app.helpers import (
    render_template, 
    log_info,
    toint
)
from app.database import db
from app.forms.admin.auth import AdminUsersForm
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

    form = AdminUsersForm(request.form)
    for name, field in iteritems(form._fields):
        log_info('name:%s, type:%s, field_type:%s' % (name, field.type, type(field)))
        log_info(field)
        for validator in field.validators:
            log_info(validator)
            log_info('--------------------')

    return render_template('admin/auth/admin_user_detail.html.j2', form=form)


@auth.route('/edit/<int:admin_uid>')
def edit(admin_uid):
    """编辑管理员"""
    g.page_title = _(u'管理员详情')

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
    form = AdminUsersForm(request.form)
    if not form.validate():
        log_info(form.errors)
        return render_template('admin/auth/admin_user_detail.html.j2', form=form)

    return 'save'

