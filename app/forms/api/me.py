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


class AddressForm(FlaskForm):
    """收货地址form"""
    ua_id      = IntegerField()
    name       = StringField(validators=[Required(message=_(u'请填写姓名'))])
    mobile     = StringField(validators=[Required(message=_(u'请填写手机号码'))])
    province   = StringField(validators=[Required(message=_(u'请填写省份'))])
    city       = StringField(validators=[Required(message=_(u'请填写城市'))])
    district   = StringField(validators=[Required(message=_(u'请填写行政区'))])
    address    = StringField(validators=[Required(message=_(u'请填写详细地址'))])
    is_default = IntegerField()
