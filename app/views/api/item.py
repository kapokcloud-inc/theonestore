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
    Blueprint
)

from app.helpers import (
    log_info,
    toint
)
from app.helpers.user import get_uid

from app.services.response import ResponseJson
from app.services.api.item import (
    ItemService, 
    ItemListService,
    CategoryService
)

item = Blueprint('api.item', __name__)

resjson = ResponseJson()
resjson.module_code = 11


@item.route('/goods')
def goods():
    """ 商品列表分页
        @param cat_id, 商品分类id 0=全部分类
        @cat_id is_hot, 是否热卖 0=默认 1=非热卖 2=热卖
        @param is_recommend, 是否推荐 0=默认 1=非推荐 2=推荐
    """
    resjson.action_code = 10
    params = request.args.to_dict()

    p = toint(params.get('p', '1'))
    ps = toint(params.get('ps', '10'))
    cat_id = toint(params.get('cat_id', '0'))
    is_hot = toint(params.get('is_hot', '0'))
    is_recommend = toint(params.get('is_recommend', '0'))

    if cat_id < 0 or p <= 0 or ps <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    if not is_hot in [0, 1, 2]:
        return resjson.print_json(resjson.PARAM_ERROR)

    if not is_recommend in [0, 1, 2]:
        return resjson.print_json(resjson.PARAM_ERROR)

    is_hot = 1 if is_hot == 2 else 0
    is_recommend = 1 if is_recommend == 2 else 0
    item_list_service = ItemListService(
                            page=p,
                            page_size=ps,
                            cat_id=cat_id, 
                            is_hot=is_hot, 
                            is_recommend=is_recommend)
    items = item_list_service.items()

    cat_service = CategoryService()
    cat = cat_service.get_category(cat_id)

    data = {'goods': items, 'current_cate': cat}
    return resjson.print_json(0, u'ok', data)


@item.route('/detail')
def detail():
    """ 商品详情
    @param goods_id, 商品id
    """
    resjson.action_code = 11

    goods_id = toint(request.args.get('goods_id', '0'))
    if goods_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    uid = get_uid()
    service = ItemService(goods_id, uid)
    return resjson.print_json(0, 'ok', {
            'item': service.item,
            'galleries': service.galleries,
            'is_fav': service.is_fav,
            'comments': service.comments(1, 12),
            'rating_1_count': service.get_rating_count(1),
            'rating_2_count': service.get_rating_count(2),
            'rating_3_count': service.get_rating_count(3),
            'img_count': service.get_image_rating_count(),
            'cart_num': service.cart_num()
    })
