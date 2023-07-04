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
from flask_uploads import (
    UploadSet,
    IMAGES
)
from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    SelectField,
    TextAreaField,
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

from app.database import db

from app.helpers import (
    render_template,
    log_info,
    toint
)

from app.forms import Form

from app.models.item import GoodsCategories


class ItemForm(Form):
    """商品form"""
    goods_id = HiddenField(default=0)
    cat_id = SelectField(
        _(u'分类'),
        coerce=int,
        validators=[
            Required(message=_(u'请选择商品分类'))
        ]
    )
    goods_name = StringField(
        _(u'商品名称'),
        validators=[
            Required(message=_(u'请填写商品名称'))
        ]
    )
    goods_img = FileField(
        _(u'封面原图'),
        description=_(u'请上传不小于800x800正方形图片'),
        validators=[
            FileRequired(_(u'文件未上传')),
            FileAllowed(UploadSet('images', IMAGES),
                        message=_(u'只允许上传图片'))
        ]
    )
    goods_desc = TextAreaField(_(u'商品简介'))
    goods_price = DecimalField(
        _(u'商品金额'),
        validators=[
            Required(message=_(u'请填写商品金额')),
            NumberRange(min=0, message=_(u'金额不能小于0'))
        ]
    )
    market_price = DecimalField(
        _(u'市场价格'),
        default=0.00,
        description=_(u'设置为0不显示'),
        validators=[
            NumberRange(min=0, message=_(u'金额不能小于0'))
        ]
    )
    stock_quantity = IntegerField(
        _(u'库存数量'),
        validators=[
            Required(message=_(u'请填写库存数量')),
            NumberRange(min=0, message=_(u'商品库存不能小于0'))
        ]
    )
    is_sale = BooleanField(_(u'是否在售'), false_values=(0, '0', ''))
    is_hot = BooleanField(_(u'是否热门商品'), false_values=(0, '0', ''))
    is_recommend = BooleanField(_(u'是否推荐'), false_values=(0, '0', ''))

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        _categories = db.session.query(
            GoodsCategories.cat_id, GoodsCategories.cat_name).all()
        _categories = [(category.cat_id, category.cat_name)
                       for category in _categories]
        self.cat_id.choices = _categories


class ItemH5Form(FlaskForm):
    """商品H5form"""
    goods_id = IntegerField()


class ItemGalleriesForm(FlaskForm):
    """商品相册form"""
    goods_id = IntegerField()


class CategoryForm(Form):
    """分类form"""
    cat_id = HiddenField(default=0)
    cat_name = StringField(
        _(u'分类名称'),
        render_kw={'placeholder': _(u'请输入分类名称')},
        validators=[
            Required(message=_(u'必填项'))
        ]
    )
    cat_img = FileField(
        _(u'分类图片'),
        description=_(u'请上传不小于400x400正方形图片'),
        validators=[
            FileRequired(_(u'文件未上传')),
            FileAllowed(UploadSet('images', IMAGES),
                        message=_(u'只允许上传图片'))
        ]
    )
    is_show = BooleanField(_(u'是否显示'), false_values=(0, '0', ''), default=1)
    is_recommend = BooleanField(_(u'推荐到电脑版导航栏'), false_values=(0, '0', ''))
