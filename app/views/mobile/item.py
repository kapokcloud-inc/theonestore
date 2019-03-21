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

from app.helpers import (
    render_template,
    log_info,
    toint
)
from app.helpers.user import get_uid
from app.services.api.item import (
    ItemService, 
    ItemListService,
    CategoryService
)


item = Blueprint('mobile.item', __name__)

@item.route('/')
def index():
    """商品列表页"""
    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))
    cat_id = toint(args.get('cat_id', '0'))
    is_hot = toint(args.get('is_hot', '0'))
    is_recommend = toint(args.get('is_recommend', '0'))

    service = ItemListService(p, ps, 
                cat_id = cat_id, 
                is_hot = is_hot, 
                is_recommend = is_recommend)
    items = service.items()

    cs = CategoryService()
    cat = cs.get_category(cat_id)
    return render_template('mobile/item/index.html.j2', 
                items = items,
                pagination = service.pagination,
                category = cat,
                paging_url = url_for('mobile.item.paging', **args))


@item.route('/paging')
def paging():
    """加载分页"""
    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))
    cat_id = toint(args.get('cat_id', '0'))
    is_hot = toint(args.get('is_hot', '0'))
    is_recommend = toint(args.get('is_recommend', '0'))

    service = ItemListService(p, ps, 
                cat_id = cat_id, 
                is_hot = is_hot, 
                is_recommend = is_recommend)
    items = service.items()

    return render_template('mobile/item/paging.html.j2', 
                items = items)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """商品详情页"""
    uid   = get_uid()
    service = ItemService(goods_id, uid)
    return render_template('mobile/item/detail.html.j2',
                item = service.item,
                galleries = service.galleries,
                is_fav = service.is_fav,
                comments = service.comments(1, 12),
                pagination = service.comment_pagination(1, 12),
                rating_1_count = service.get_rating_count(1),
                rating_2_count = service.get_rating_count(2),
                rating_3_count = service.get_rating_count(3),
                img_count = service.get_image_rating_count()
    )


@item.route('/recommend')
def recommend():
    """推荐"""
    service = ItemListService(1, 10, is_recommend=1)
    items = service.items()
    return render_template('mobile/item/recommend.html.j2', 
                items = items,
                pagination = service.pagination,
                paging_url = url_for('mobile.item.paging', is_recommend=1))


@item.route('/hot')
def hot():
    """热卖"""
    service = ItemListService(1, 10, is_hot=1)
    items = service.items()
    return render_template('mobile/item/hot.html.j2', 
                items = items,
                pagination = service.pagination,
                paging_url = url_for('mobile.item.paging', is_hot=1))
