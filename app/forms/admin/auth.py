# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_wtf.file import (
    FileField, 
    FileAllowed, 
    FileRequired, 
    FileStorage
)
from wtforms import (
    StringField,
    PasswordField,
    HiddenField
)
from wtforms.widgets.core import (
    TextArea,
    TextInput,
    PasswordInput
)
from wtforms.validators import (
    Required,
    Length,
    EqualTo,
    NumberRange
)
from flask_uploads import UploadSet, IMAGES

from app.helpers import toint, log_info
from app.forms import Form
from app.models.auth import AdminUsers

class AdminUsersEditForm(Form):
    """编辑管理员form"""
    admin_uid = HiddenField(default=0)

    username = StringField(_(u'用户名'), validators=[
                    Required(message=_(u'必填项')), 
                    Length(min=3, max=10, message=_(u'用户名长度在3至10位'))
                ])

    mobile = StringField(_(u'手机号码'), validators=[
                    Required(message=_(u'必填项')), 
                    Length(min=11, max=11, message=_(u'手机号码长度只能为11位'))
                ])

    avatar = FileField(_(u'头像'), 
                    description=_(u'一张靓照'), validators=[
                    FileRequired(_(u'文件未上传')), 
                    FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片'))
                ])

    def validate_on_submit(self):
        """检验表单"""
        ret = super(AdminUsersEditForm, self).validate_on_submit()
        if ret is False:
            return ret

        admin_uid = toint(self.admin_uid.data)
        au = AdminUsers.query.filter(AdminUsers.username == self.username.data).first()
        if au is not None and au.admin_uid != admin_uid:
            self.username.errors = (_(u'用户名已经存在'),)
            ret = False

        au = AdminUsers.query.filter(AdminUsers.mobile == self.mobile.data).first()
        if au is not None and au.admin_uid != admin_uid:
            self.mobile.errors = (_(u'手机号码已经存在'),)
            ret = False         

        return ret


class AdminUsersForm(AdminUsersEditForm):
    """管理员form"""
    password = PasswordField(_(u'密码'), validators=[
                    Required(message=_(u'必填项')), 
                    Length(min=6, max=20, message=_(u'密码长度在6位至20位')),
                    EqualTo('password2', message=_(u'密码不相同'))
                ])

    password2 = PasswordField(_(u'重复密码'), validators=[
                    Required(message=_(u'必填项')), 
                    Length(min=6, max=20, message=_(u'密码长度在6位至20位')),
                    EqualTo('password', message=_(u'密码不相同'))
                ])
