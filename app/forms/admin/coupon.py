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
    SelectField,
    TextAreaField,
    DateField,
    HiddenField,
    BooleanField
)
from wtforms.validators import (
    DataRequired as Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)

from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.forms import Form


class CouponBatchForm(Form):
    """优惠券form"""
    cb_id            = HiddenField(default=0)

    cb_name          = StringField(
                            _(u'批次名称'),
                            validators=[
                                Required(message=_(u'请填写批次名称'))
                            ]
                        )

    coupon_name      = StringField(
                            _(u'优惠券名称'),
                            validators=[
                                Required(message=_(u'请填写优惠券名称'))
                            ]
                        )

    begin_time       = StringField(
                            _(u'开始时间'),
                            render_kw={'class':'form-control datepicker-autoclose'}
                        )

    end_time         = StringField(
                            _(u'结束时间'),
                            render_kw={'class':'form-control datepicker-autoclose'}
                        )

    is_valid         = BooleanField(_(u'是否有效'), false_values=(0, '0', ''))

    publish_num      = IntegerField(
                            _(u'发行数量'),
                            validators=[
                                NumberRange(min=0, message=_(u'不能小于0'))
                            ]
                        )

    coupon_amount    = DecimalField(
                            _(u'优惠券金额'),
                            validators=[
                                NumberRange(min=0, message=_(u'金额不能小于0'))
                            ]
                        )

    limit_amount     = DecimalField(
                            _(u'满减额度'),
                            validators=[
                                NumberRange(min=0, message=_(u'金额不能小于0'))
                            ]
                        )

    date_num         = IntegerField(
                            _(u'每天最大赠送数'),
                            validators=[
                                NumberRange(min=0, message=_(u'不能小于0'))
                            ]
                        )

    coupon_from      = StringField(_(u'优惠券来源说明'))
