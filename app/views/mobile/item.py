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

from app.services.api.item import ItemStaticMethodsService

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


item = Blueprint('mobile.item', __name__)

@item.route('/')
def index():
    """商品列表页"""

    items      = ItemStaticMethodsService.items(request.args.to_dict())
    paging_url = url_for('mobile.item.paging', **request.args)

    return render_template('mobile/item/index.html.j2', items=items, paging_url=paging_url)


@item.route('/paging')
def paging():
    """加载分页"""

    items = ItemStaticMethodsService.items(request.args.to_dict())

    return render_template('mobile/item/paging.html.j2', items=items)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """ 商品详情页 """
    return render_template('mobile/item/detail.html.j2')


@item.route('/recommend')
def recommend():
    """ 推荐 """
    return render_template('mobile/item/recommend.html.j2')


@item.route('/hot')
def hot():
    """ 热卖 """
    return render_template('mobile/item/hot.html.j2')
