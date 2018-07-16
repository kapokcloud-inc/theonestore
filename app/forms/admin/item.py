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
    TextAreaField
)
from wtforms.validators import (
    Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)

from app.database import db
from app.models.item import GoodsCategories
from app.helpers import (
    render_template, 
    log_info,
    toint
)


class ItemForm(FlaskForm):
    """商品form"""
    goods_id       = IntegerField()
    cat_id         = SelectField(
                        coerce=int,
                        validators=[
                            Required(message=_(u'请选择商品分类'))]
                    )
    goods_name     = StringField(
                        validators=[
                            Required(message=_(u'请填写商品名称'))]
                    )
    goods_desc     = TextAreaField()
    goods_price    = DecimalField(
                        validators=[
                            NumberRange(min=0, message=_(u'金额不能小于0'))]
                    )
    market_price   = DecimalField(
                        validators=[
                            NumberRange(min=0, message=_(u'金额不能小于0'))]
                    )
    is_sale        = SelectField(
                        coerce=int,
                        choices=[(0, _(u'否')), (1, _(u'是'))]
                    )
    stock_quantity = IntegerField(
                        validators=[
                            NumberRange(min=0, message=_(u'商品库存不能小于0'))]
                    )
    is_hot         = SelectField(
                        coerce=int,
                        choices=[(0, _(u'否')), (1, _(u'是'))]
                    )
    is_recommend   = SelectField(
                        coerce=int,
                        choices=[(0, _(u'否')), (1, _(u'是'))]
                    )

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        _categories = db.session.query(GoodsCategories.cat_id, GoodsCategories.cat_name).all()
        _categories = [(category.cat_id, category.cat_name) for category in _categories]
        self.cat_id.choices = _categories


class ItemH5Form(FlaskForm):
    """商品H5form"""
    goods_id = IntegerField()


class ItemGalleriesForm(FlaskForm):
    """商品相册form"""
    goods_id = IntegerField()


class CategoryForm(FlaskForm):
    """分类form"""
    cat_id   = IntegerField()
    cat_name = StringField(
                    _(u'分类名称'), 
                    render_kw={'placeholder':_(u'请输入分类名称')},
                    validators=[
                        InputRequired(message=_(u'必填项'))]
                )
    """cat_img   = FileField(
                    _(u'分类图片'),
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(IMAGES, message=_(u'只能上传图片'))]
                )"""

