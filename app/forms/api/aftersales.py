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


class checkOrderId(object):
    def __init__(self, message=_(u'参数错误')):
        self.message = message

    def __call__(self, form, field):
        if form.og_id.data == 0 and field.data == 0:
            raise ValidationError(self.message)


class AfterSalesForm(FlaskForm):
    """售后form"""
    order_id        = IntegerField(validators=[checkOrderId()])
    og_id           = IntegerField()
    aftersales_type = IntegerField()
    deliver_status  = IntegerField()
    img_data        = StringField()
    content         = StringField(validators=[Required(message=_(u'请填写申请原因'))])


class AfterSalesAddressForm(FlaskForm):
    """售后地址form"""
    ua_id      = IntegerField()
    name       = StringField(validators=[Required(message=_(u'请填写姓名'))])
    mobile     = StringField(validators=[Required(message=_(u'请填写手机号码'))])
    province   = StringField(validators=[Required(message=_(u'请填写省份'))])
    city       = StringField(validators=[Required(message=_(u'请填写城市'))])
    district   = StringField(validators=[Required(message=_(u'请填写行政区'))])
    address    = StringField(validators=[Required(message=_(u'请填写详细地址'))])
