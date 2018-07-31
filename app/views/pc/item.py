# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    render_template,
    log_info
)
from app.helpers.user import get_uid

from app.services.api.comment import CommentStaticMethodsService
from app.services.api.item import ItemStaticMethodsService

from app.models.like import Like
from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('pc.item', __name__)

@item.route('/')
def index():
    """pc - 商品列表页"""

    categorys = ItemStaticMethodsService.categories({'cat_id':request.args.to_dict().get('cat_id')})
    items, pagination = ItemStaticMethodsService.items(request.args.to_dict())
    paging_url        = url_for('pc.item.paging', **request.args)

    if categorys:
        currentCate = categorys[0]

    return render_template('pc/item/index.html.j2', currentCate=currentCate, items=items, paging_url=paging_url)


@item.route('/paging')
def paging():
    """加载分页"""

    items, pagination = ItemStaticMethodsService.items(request.args.to_dict())

    return render_template('pc/item/paging.html.j2', items=items)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """ pc - 商品详情页 """

    uid = get_uid()
    if not uid:
        session['weixin_login_url'] = request.url

    item      = Goods.query.get_or_404(goods_id)
    galleries = db.session.query(GoodsGalleries.img).filter(GoodsGalleries.goods_id == goods_id).all()

    is_fav = db.session.query(Like.like_id).\
                filter(Like.like_type == 2).\
                filter(Like.ttype == 1).\
                filter(Like.tid == goods_id).\
                filter(Like.uid == uid).first()
    is_fav = 1 if is_fav else 0

    comments = []
    if item.comment_count > 0:
        comments = CommentStaticMethodsService.comments({'p':1, 'ps':2, 'ttype':1, 'tid':goods_id})

    return render_template('pc/item/detail.html.j2', item=item, galleries=galleries, is_fav=is_fav, comments=comments)


@item.route('/recommend')
def recommend():
    """pc - 推荐"""

    params            = {'is_recommend':1}
    items, pagination = ItemStaticMethodsService.items(params)
    paging_url        = url_for('pc.item.paging', **params)

    return render_template('pc/item/recommend.html.j2', items=items, paging_url=paging_url)


@item.route('/hot')
def hot():
    """pc - 热卖"""

    params            = {'is_hot':1}
    items, pagination = ItemStaticMethodsService.items(params)
    paging_url        = url_for('pc.item.paging', **params)

    return render_template('pc/item/hot.html.j2', items=items, paging_url=paging_url)
