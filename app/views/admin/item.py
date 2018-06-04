# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import json

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.forms.admin.item import (
    ItemForm,
    CategoryForm
)

from app.services.admin.config import (
    SmsYunpianForm,
    SmsAlismsForm,
    StorageQiniuForm,
    StorageAliossForm
)

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('admin.item', __name__)

@item.route('/')
@item.route('/<int:page>')
@item.route('/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """商品列表"""

    args       = request.args
    cat_id     = toint(args.get('cat_id', '0'))
    is_sale    = args.get('is_sale', '-1')
    is_sale    = toint(is_sale) if is_sale in ['-1', '0', '1'] else -1
    is_hot     = args.get('is_hot', '-1')
    is_hot     = toint(is_hot) if is_hot in ['-1', '0', '1'] else -1
    goods_name = args.get('goods_name', '').strip()

    q = db.session.query(Goods.goods_id, Goods.cat_id, Goods.goods_name, Goods.goods_img, Goods.goods_price, 
                         Goods.is_sale, Goods.stock_quantity, Goods.is_hot, Goods.is_recommend, Goods.add_time,
                         GoodsCategories.cat_name).\
        filter(Goods.cat_id == GoodsCategories.cat_id).\
        filter(Goods.is_delete == 0)

    if cat_id > 0:
        q = q.filter(Goods.cat_id == cat_id)
    
    if is_sale in [0,1]:
        q = q.filter(Goods.is_sale == is_sale)
    
    if is_hot in [0,1]:
        q = q.filter(Goods.is_hot == is_hot)
    
    if goods_name:
        q = q.filter(Goods.goods_name.like('%%%s%%' % goods_name))
    
    items      = q.order_by(Goods.goods_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    cats  = [{'name':_(u'请选择……'), 'value':'-1'}]
    _cats = db.session.query(GoodsCategories.cat_id, GoodsCategories.cat_name).\
                order_by(GoodsCategories.cat_id.desc()).all()
    for _cat in _cats:
        cat = {'name':_cat.cat_name, 'value':_cat.cat_id}
        cats.append(cat)

    return render_template('admin/item/index.html.j2', pagination=pagination, items=items, cats=cats)


@item.route('/create')
def create():
    """新增商品"""

    wtf_form = ItemForm()

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item={})


@item.route('/detail/<int:goods_id>')
def detail(goods_id):
    """商品详情"""

    wtf_form = ItemForm()
    item     = Goods.query.get_or_404(goods_id)

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item=item)


@item.route('/save', methods=['POST'])
def save():
    """保存商品"""

    wtf_form = ItemForm()

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item=item)


@item.route('/categories')
@item.route('/categories/<int:page>')
@item.route('/categories/<int:page>-<int:page_size>')
def categories(page=1, page_size=20):
    """分类列表"""

    q = GoodsCategories.query
    
    categories = q.order_by(GoodsCategories.cat_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/item/categories.html.j2', pagination=pagination, categories=categories)


@item.route('/category/create')
def category_create():
    """新增分类"""

    wtf_form = ItemForm()

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category={})


@item.route('/category/detail/<int:cat_id>')
def category_detail(cat_id):
    """分类详情"""

    wtf_form     = ItemForm()
    category = GoodsCategories.query.get_or_404(cat_id)

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category=category)


@item.route('/category/save', methods=['POST'])
def category_save():
    """保存分类"""

    wtf_form = CategoryForm()

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category=category)

