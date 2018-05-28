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
from wtforms import (
    StringField,
    PasswordField,
    FileField,
)
from wtforms.validators import (
    Required,
    Length,
    EqualTo,
)

class AdminUsersForm(FlaskForm):
    """管理员form"""
    username = StringField(validators=[Length(min=3, max=10, message=_(u'用户名长度在3至10位'))])
    


