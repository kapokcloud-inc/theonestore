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
from flask_uploads import UploadSet, IMAGES
from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    FileField,
    SelectField,
    TextAreaField,
    DateField
)
from wtforms.validators import (
    Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange,
    ValidationError
)


class UploadImageForm(FlaskForm):
    """上传图片form"""
    prefix = StringField(validators=[Required(message=_(u'缺少前缀'))])
    image  = FileField(_(u'图片'),
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片'))
                    ])
