# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_uploads import IMAGES
from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    HiddenField,
    BooleanField
)
from wtforms.validators import (
    DataRequired as Required,
    InputRequired,
    ValidationError
)
from app.forms import Form


class checkFree(object):
    def __init__(self, message=_(u'金额不能小于或等于0')):
        self.message = message

    def __call__(self, form, field):
        if form.is_free.data == 0 and field.data <= 0:
            raise ValidationError(self.message)


class ShippingForm(Form):
    """快递form"""
    shipping_id = HiddenField(default=0, validators=[Required(message=_(u'请选择快递id'))])

    shipping_name = StringField(label=_(u'快递名称'), render_kw={'disabled':''})

    is_free = BooleanField(label=_(u'是否免运费'),
                description=_(u'免运费'),
                false_values=(0, '0', ''))

    shipping_amount = DecimalField(label=_(u'邮费'),
                        validators=[InputRequired(message=_(u'必填项')), checkFree()])

    free_limit_amount = DecimalField(label=_(u'满多少包邮'),validators=[checkFree()])

    is_enable = BooleanField(label=_(u'是否启用'),
                    description=_(u'启用'),
                    false_values=(0, '0', ''))

    is_default = BooleanField(label=_(u'是否默认快递'),
                    description=_(u'默认快递'),
                    false_values=(0, '0', ''))

    sorting = IntegerField(label=_(u'排序'), 
                default=50,
                description=_(u'数值越大排序越靠前'),
                validators=[Required(message=_(u'必填项'))]
                )

