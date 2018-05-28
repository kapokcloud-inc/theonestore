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

from flask_babel import gettext as _

from app.helpers import log_info
from app.models.auth import AdminUsers


class AuthLoginService(object):
    """授权登录服务"""
    def _init_(self):
        """初始化"""
        self.errmsg = {}
        self.admin_user = None

        pass

    def login(self, mobile, password):
        """登录"""
        self.errmsg = {}
        if not mobile:
            self.errmsg['mobile'] = _(u'手机号码/帐号不能为空')
        if not password:
            self.errmsg['password'] = _(u'密码不能为空')
        if password and len(password) != 64:
            self.errmsg['password'] = _(u'密码哈希值长度错误')

        if not self.errmsg:
            self.admin_user = AdminUsers.query.filter(AdminUsers.mobile == mobile).first()
            if not self.admin_user:
                self.admin_user = AdminUsers.query.filter(AdminUsers.username == mobile).first()

            if not self.admin_user:
                self.errmsg['mobile'] = _(u'手机号码/帐号不存在')
            else:
                sha_password = sha256(password + self.admin_user.salt).hexdigest()
                if sha_password != self.admin_user.password:
                    self.errmsg['password'] = _(u'密码错误')

        ret = (False if self.errmsg else True)
        log_info(u'[AuthLoginService] [login] mobile/username:%s, return:%s, errmsg:%s, admin_user:%s' % (
            mobile, ret, self.errmsg, self.admin_user))

        return ret


    def write_session(self, session):
        """登录成功后写session"""
        if self.admin_user:
            # 登录信息写到session
            session['admin_uid'] = self.admin_user.admin_uid
            session['admin_gid'] = self.admin_user.admin_gid
            session['username'] = self.admin_user.username
            session['mobile'] = self.admin_user.mobile
            session['avatar'] = self.admin_user.avatar


class SaveAdminUsersService(object):
    """保存管理员用户service"""
    def __init__(self):
        self.admin_user = None
        self.current_time = int(time.time())

    
    