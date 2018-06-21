# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileField, 
    FileAllowed, 
    FileRequired, 
    FileStorage
)
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField
)
from wtforms.widgets.core import (
    TextArea,
    TextInput,
    PasswordInput
)
from wtforms.validators import (
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)
from flask_uploads import IMAGES


class AdminUsersForm(FlaskForm):
    """管理员form"""
    username = StringField(_(u'用户名'), 
                description=_(u'详细用户名'),
                render_kw={'placeholder':_(u'请输入用户名')},
                validators=[
                    InputRequired(message=_(u'必填项')), 
                    Length(min=3, max=10, message=_(u'用户名长度在3至10位'))
                ])

    mobile = StringField(_(u'手机号码'), validators=[
                    InputRequired(message=_(u'必填项')), 
                    Length(min=11, max=11, message=_(u'手机号码长度只能为11位'))
                ])

    password = PasswordField(_(u'密码'), validators=[
                    InputRequired(message=_(u'必填项')), 
                    Length(min=6, max=20, message=_(u'密码长度在6位至20位'))
                ])

    password2 = PasswordField(_(u'重复密码'), validators=[EqualTo(password, message=_(u'密码不相同'))])

    avatar = FileField(_(u'头像'), validators=[
                    FileRequired(_(u'文件未上传')), 
                    FileAllowed(IMAGES, message=_(u'只能上传图片'))
                ])
    
