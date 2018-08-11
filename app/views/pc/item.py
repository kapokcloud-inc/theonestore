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

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('pc.item', __name__)

@item.route('/')
def index():
    """商品列表页"""

    data = ItemStaticMethodsService.items(request.args.to_dict(),True)

    return render_template('pc/item/index.html.j2', **data)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """商品详情页"""

    uid  = get_uid()
    data = ItemStaticMethodsService.detail_page(goods_id, uid)

    return render_template('pc/item/detail.html.j2', **data)


@item.route('/recommend')
def recommend():
    """推荐"""

    data = ItemStaticMethodsService.items(request.args.to_dict(),True)

    return render_template('pc/item/recommend.html.j2', **data)


@item.route('/hot')
def hot():
    """热卖"""

    data = ItemStaticMethodsService.items(request.args.to_dict(),True)

    return render_template('pc/item/hot.html.j2', **data)


@item.route('/comments-paging')
def comments_paging():
    """加载评论分页"""

    query_string = request.args.get('query_string')
    query_list = query_string.split('&')

    params = {}
    for _str in query_list:
        _list = _str.split('=')
        params[_list[0]] = _list[1]

    _data      = CommentStaticMethodsService.comments(params, True)
    comments   = _data['comments']
    pagination = _data['pagination']

    data = {'comments':comments, 'pagination':pagination, 'params':params}
    return render_template('pc/item/comments_paging.html.j2', **data)
