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
    NumberRange
)

from app.database import db
from app.forms.admin import NotExist
from app.helpers import (
    render_template, 
    log_info,
    toint
)


class CouponBatchForm(FlaskForm):
    """优惠券form"""
    cb_id            = IntegerField()
    cb_name          = StringField(
                        validators=[
                            Required(message=_(u'请填写批次名称'))]
                        )
    coupon_name      = StringField(
                        validators=[
                            Required(message=_(u'请填写优惠券名称'))]
                        )
    begin_time       = StringField()
    end_time         = StringField()
    is_valid         = SelectField(
                        coerce=int,
                        choices=[(0, _(u'否')), (1, _(u'是'))]
                        )
    publish_num      = IntegerField(
                        validators=[
                            NumberRange(min=0, message=_(u'不能小于0'))]
                        )
    coupon_amount    = DecimalField(
                        validators=[
                            NumberRange(min=0, message=_(u'金额不能小于0'))]
                        )
    limit_amount     = DecimalField(
                        validators=[
                            NumberRange(min=0, message=_(u'金额不能小于0'))]
                        )
    limit_goods      = StringField()
    limit_goods_name = StringField()
    date_num         = IntegerField(
                        validators=[
                            NumberRange(min=0, message=_(u'不能小于0'))]
                        )
    coupon_from      = StringField()

