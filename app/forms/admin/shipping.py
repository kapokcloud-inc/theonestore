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


class checkFree(object):
    def __init__(self, message=_(u'金额不能小于或等于0')):
        self.message = message

    def __call__(self, form, field):
        if form.is_free.data == 0 and field.data <= 0:
            raise ValidationError(self.message)


class ShippingForm(FlaskForm):
    """快递form"""
    shipping_id       = IntegerField()
    shipping_name     = StringField()
    is_free           = SelectField(
                            coerce=int,
                            choices=[(0, _(u'否')), (1, _(u'是'))]
                        )
    shipping_amount   = DecimalField(
                            validators=[checkFree()]
                        )
    free_limit_amount = DecimalField(
                            validators=[checkFree()]
                        )
    is_enable         = SelectField(
                            coerce=int,
                            choices=[(0, _(u'否')), (1, _(u'是'))]
                        )
    is_default        = SelectField(
                            coerce=int,
                            choices=[(0, _(u'否')), (1, _(u'是'))]
                        )
    sorting           = IntegerField()

