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


class checkFree(object):
    def __init__(self, message=_(u'金额不能小于或等于0')):
        self.message = message

    def __call__(self, form, field):
        if form.is_free.data == 0 and field.data <= 0:
            raise ValidationError(self.message)


class AddressForm(FlaskForm):
    """收货地址form"""
    ua_id      = IntegerField()
    name       = StringField(validators=[Required(message=_(u'请填写姓名'))])
    mobile     = StringField(validators=[Required(message=_(u'请填写手机号码'))])
    province   = StringField(validators=[Required(message=_(u'请填写省份'))])
    city       = StringField(validators=[Required(message=_(u'请填写城市'))])
    district   = StringField(validators=[Required(message=_(u'请填写行政区'))])
    address    = StringField(validators=[Required(message=_(u'请填写详细地址'))])
    zip        = StringField()
    is_default = IntegerField(validators=[NumberRange(min=0, max=1)])
