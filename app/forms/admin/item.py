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
)
from wtforms.validators import (
    Required,
    Length,
    EqualTo,
)

class ItemForm(FlaskForm):
    """商品form"""
    goods_id   = IntegerField()
    goods_name = StringField(validators=[Required(message=_(u'请填写商品名称'))])


class CategoryForm(FlaskForm):
    """分类form"""
    cat_id   = IntegerField()
    cat_name = StringField(validators=[Required(message=_(u'请填写分类名称'))])

