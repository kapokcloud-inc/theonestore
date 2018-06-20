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
from flask_uploads import IMAGES
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

from app.database import db
from app.helpers import (
    render_template, 
    log_info,
    toint
)


class checkTtype(object):
    def __init__(self, message=_(u'请完善跳转信息或填写外部链接')):
        self.message = message

    def __call__(self, form, field):
        if field.data <= 0 and form.url.data == '':
            raise ValidationError(self.message)


class checkTid(object):
    def __init__(self, message=_(u'请填写跳转目标')):
        self.message = message

    def __call__(self, form, field):
        if field.data <= 0 and form.ttype.data > 0:
            raise ValidationError(self.message)


class checkUrl(object):
    def __init__(self, message=_(u'请完善跳转信息或填写外部链接')):
        self.message = message

    def __call__(self, form, field):
        if field.data == '' and form.ttype.data <= 0:
            raise ValidationError(self.message)


class AdvForm(FlaskForm):
    """广告form"""
    adv_id  = IntegerField()
    ac_id   = SelectField(
                    coerce=int,
                    validators=[
                        Required(message=_(u'请选择分类'))]
                )
    desc    = StringField()
    ttype   = SelectField(
                    coerce=int,
                    validators=[
                            checkTtype()]
                )
    tid     = IntegerField(validators=[checkTid()])
    url     = StringField(validators=[checkUrl()])
    sorting = StringField()
    is_show = SelectField(coerce=int, choices=[(0, _(u'否')), (1, _(u'是'))])

