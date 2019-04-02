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
    log_info,
    toint
)
from app.helpers.user import get_uid

from app.services.api.comment import CommentStaticMethodsService
from app.services.api.item import (
    ItemService,
    ItemListService,
    CategoryService
)

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('pc.item', __name__)


@item.route('/')
def index():
    """商品列表页"""
    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))
    cat_id = toint(args.get('cat_id', '0'))
    is_hot = toint(args.get('is_hot', '0'))
    is_recommend = toint(args.get('is_recommend', '0'))
    search_key = args.get('search_key').strip()

    service = ItemListService(
        p,
        ps,
        cat_id=cat_id,
        is_hot=is_hot,
        is_recommend=is_recommend,
        search_key=search_key)
    items = service.items()

    cs = CategoryService()
    cat = cs.get_category(cat_id)
    return render_template(
        'pc/item/index.html.j2',
        items=items,
        pagination=service.pagination,
        category=cat)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """商品详情页"""
    uid = get_uid()
    service = ItemService(goods_id, uid)
    return render_template(
        'pc/item/detail.html.j2',
        item=service.item,
        galleries=service.galleries,
        is_fav=service.is_fav,
        comments=service.comments(1, 12),
        pagination=service.comment_pagination(1, 12),
        rating_1_count=service.get_rating_count(1),
        rating_2_count=service.get_rating_count(2),
        rating_3_count=service.get_rating_count(3),
        img_count=service.get_image_rating_count(),
        cart_num=service.cart_num
    )


@item.route('/recommend')
def recommend():
    """推荐"""
    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))
    service = ItemListService(p, ps, is_recommend=1)
    items = service.items()
    return render_template(
        'pc/item/recommend.html.j2',
        items=items,
        pagination=service.pagination)


@item.route('/hot')
def hot():
    """热卖"""
    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))
    service = ItemListService(p, ps, is_hot=1)
    items = service.items()
    return render_template(
        'pc/item/hot.html.j2',
        items=items,
        pagination=service.pagination)


@item.route('/comments-paging')
def comments_paging():
    """加载评论分页"""

    query_string = request.args.get('query_string')
    query_list = query_string.split('&')

    params = {}
    for _str in query_list:
        _list = _str.split('=')
        params[_list[0]] = _list[1]

    _data = CommentStaticMethodsService.comments(params, True)
    comments = _data['comments']
    pagination = _data['pagination']

    data = {
        'comments': comments,
        'pagination': pagination,
        'params': params}
    return render_template('pc/item/comments_paging.html.j2', **data)
