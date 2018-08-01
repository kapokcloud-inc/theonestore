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

    data               = ItemStaticMethodsService.items(request.args.to_dict())
    data['paging_url'] = url_for('pc.item.paging', **request.args)

    return render_template('pc/item/index.html.j2', **data)


@item.route('/paging')
def paging():
    """加载分页"""

    data = ItemStaticMethodsService.items(request.args.to_dict())

    return render_template('pc/item/paging.html.j2', **data)


@item.route('/<int:goods_id>')
def detail(goods_id):
    """商品详情页"""

    uid = get_uid()
    if not uid:
        session['weixin_login_url'] = request.url

    data = ItemStaticMethodsService.detail_page(goods_id, uid)

    return render_template('pc/item/detail.html.j2', **data)


@item.route('/recommend')
def recommend():
    """推荐"""

    params             = {'is_recommend':1}
    data               = ItemStaticMethodsService.items(params)
    data['paging_url'] = url_for('pc.item.paging', **params)

    return render_template('pc/item/recommend.html.j2', **data)


@item.route('/hot')
def hot():
    """热卖"""

    params             = {'is_hot':1}
    data               = ItemStaticMethodsService.items(params)
    data['paging_url'] = url_for('pc.item.paging', **params)

    return render_template('pc/item/hot.html.j2', **data)
