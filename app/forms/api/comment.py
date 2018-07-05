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


class CommentOrderGoodsForm(FlaskForm):
    """评价订单商品form"""
    og_id    = IntegerField(validators=[Required(message=_(u'参数错误'))])
    rating   = IntegerField(validators=[NumberRange(min=1, max=3, message=_(u'请选择评分'))])
    content  = StringField(validators=[Required(message=_(u'请填写评价'))])
    img_data = StringField()
