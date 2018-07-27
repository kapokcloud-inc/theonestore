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
    url_for,
    g,
    jsonify
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    toint,
    model_update
)
from app.helpers.date_time import current_timestamp

from app.forms.admin.item import (
    ItemForm,
    ItemH5Form,
    ItemGalleriesForm,
    CategoryForm
)

from app.services.response import ResponseJson
from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('admin.item', __name__)

resjson = ResponseJson()
resjson.module_code = 13

@item.route('/index')
@item.route('/index/<int:page>')
@item.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """商品列表"""
    g.page_title = _(u'商品')

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
    """添加商品"""
    g.page_title = _(u'添加商品')

    wtf_form = ItemForm()

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item={})


@item.route('/detail/<int:goods_id>')
def detail(goods_id):
    """商品详情"""
    g.page_title = _(u'商品详情')

    item = Goods.query.get_or_404(goods_id)

    wtf_form                   = ItemForm()
    wtf_form.cat_id.data       = item.cat_id
    wtf_form.is_sale.data      = item.is_sale
    wtf_form.is_hot.data       = item.is_hot
    wtf_form.is_recommend.data = item.is_recommend
    wtf_form.goods_desc.data   = item.goods_desc

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item=item)


@item.route('/save', methods=['POST'])
def save():
    """保存商品"""
    g.page_title = _(u'保存商品')

    current_time = current_timestamp()
    wtf_form     = ItemForm()

    if wtf_form.validate_on_submit():
        goods_id = wtf_form.goods_id.data
        if goods_id:
            item = Goods.query.get_or_404(goods_id)
        else:
            item          = Goods()
            item.detail   = ''
            item.add_time = current_time
            db.session.add(item)

        item.cat_id          = wtf_form.cat_id.data
        item.goods_name      = wtf_form.goods_name.data
        item.goods_desc      = wtf_form.goods_desc.data
        item.goods_price     = wtf_form.goods_price.data
        item.market_price    = wtf_form.market_price.data
        item.is_sale         = wtf_form.is_sale.data
        item.stock_quantity  = wtf_form.stock_quantity.data
        item.is_hot          = wtf_form.is_hot.data
        item.is_recommend    = wtf_form.is_recommend.data
        item.update_time     = current_time
        db.session.commit()

        return redirect(url_for('admin.item.index'))

    item = wtf_form.data

    return render_template('admin/item/detail.html.j2', wtf_form=wtf_form, item=item)


@item.route('/remove')
def remove():
    """删除商品"""
    resjson.action_code = 10

    goods_id = toint(request.args.get('goods_id', '0'))

    if goods_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    item = Goods.query.get(goods_id)
    if not item:
        return resjson.print_json(10, _(u'商品不存在'))

    if item.is_delete == 1:
        return resjson.print_json(0, u'ok')

    model_update(item, {'is_delete':1}, commit=True)

    return resjson.print_json(0, u'ok')


@item.route('/h5/<int:goods_id>')
def h5(goods_id):
    """商品H5详情"""
    g.page_title = _(u'商品详情')

    item     = Goods.query.get_or_404(goods_id)
    wtf_form = ItemH5Form()

    return render_template('admin/item/h5.html.j2', wtf_form=wtf_form, item=item)


@item.route('/h5/save', methods=['POST'])
def h5_save():
    """保存商品H5"""
    g.page_title = _(u'保存商品')

    goods_id = toint(request.form.get('goods_id', '0'))
    detail   = request.form.get('detail', '').strip()

    item = Goods.query.get_or_404(goods_id)
    item.detail = detail
    db.session.commit()

    return redirect(url_for('admin.item.index'))


@item.route('/galleries/<int:goods_id>')
def galleries(goods_id):
    """商品相册"""
    g.page_title = _(u'商品详情')

    galleries = GoodsGalleries.query.filter(GoodsGalleries.goods_id == goods_id).order_by(GoodsGalleries.id.desc()).all()
    wtf_form  = ItemGalleriesForm()

    return render_template('admin/item/galleries.html.j2', wtf_form=wtf_form, goods_id=goods_id, galleries=galleries)


@item.route('/galleries/save', methods=['POST'])
def galleries_save():
    """保存商品相册 ??"""
    g.page_title = _(u'保存商品')

    goods_id      = toint(request.form.get('goods_id', '0'))
    galleries     = request.files.getlist('galleries')
    
    for gallery in galleries:
        log_info(gallery)

    return redirect(url_for('admin.item.index'))


@item.route('/galleries/remove')
def galleries_remove():
    """删除商品相册"""
    resjson.action_code = 11

    id      = toint(request.args.get('id'))
    gallery = GoodsGalleries.query.filter(GoodsGalleries.id == id).first()
    db.session.delete(gallery)
    db.session.commit()

    #return jsonify({'ret':0, 'msg':'ok'})
    return resjson.print_json(0, u'ok', {'gallery':gallery})


@item.route('/categories')
@item.route('/categories/<int:page>')
@item.route('/categories/<int:page>-<int:page_size>')
def categories(page=1, page_size=20):
    """分类列表"""
    g.page_title = _(u'分类')

    q = GoodsCategories.query
    
    categories = q.order_by(GoodsCategories.cat_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/item/categories.html.j2', pagination=pagination, categories=categories)


@item.route('/category/create')
def category_create():
    """添加分类"""
    g.page_title = _(u'添加分类')

    wtf_form = CategoryForm()

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category={})


@item.route('/category/detail/<int:cat_id>')
def category_detail(cat_id):
    """分类详情"""
    g.page_title = _(u'分类详情')

    wtf_form = CategoryForm()
    category = GoodsCategories.query.get_or_404(cat_id)

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category=category)


@item.route('/category/save', methods=['POST'])
def category_save():
    """保存分类"""
    g.page_title = _(u'保存分类')

    wtf_form = CategoryForm()

    if wtf_form.validate_on_submit():
        cat_id = wtf_form.cat_id.data
        if cat_id:
            category = GoodsCategories.query.get_or_404(cat_id)
        else:
            category          = GoodsCategories()
            category.add_time = current_timestamp()
            db.session.add(category)

        category.cat_name = wtf_form.cat_name.data
        db.session.commit()

        return redirect(url_for('admin.item.categories'))

    category = wtf_form.data

    return render_template('admin/item/category_detail.html.j2', wtf_form=wtf_form, category=category)

