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
    Blueprint,
    json
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)

from app.helpers.user import get_uid

from app.services.response import ResponseJson

from app.services.api.item import ItemStaticMethodsService

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

    params['is_hot'] = is_hot - 1
    params['is_recommend'] = is_recommend - 1

    result = ItemStaticMethodsService.items(params, False)

    data = {'goods': result['items'], 'current_cate': result['category']}

    return resjson.print_json(0, u'ok', data)


@item.route('/detail')
def detail():
    """ 商品详情
        @param goods_id, 商品id
    """
    resjson.action_code = 11

    goods_id  = toint(request.args.to_dict().get('goods_id', '0'))

    if goods_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    uid       = get_uid()
    data      = ItemStaticMethodsService.detail_page(goods_id, uid)
    data.pop('pagination')

    return resjson.print_json(0, u'ok', data)