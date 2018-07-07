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
    Blueprint,
    request
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    model_create,
    model_update,
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_nickname,
    get_avatar
)

from app.services.response import ResponseJson
from app.services.api.order import (
    OrderCreateService,
    OrderUpdateService,
    OrderCancelService,
    OrderDeliverService
)

from app.forms.api.comment import CommentOrderGoodsForm

from app.models.comment import Comment
from app.models.order import (
    Order,
    OrderGoods
)


order = Blueprint('api.order', __name__)

resjson = ResponseJson()
resjson.module_code = 14

@order.route('/create', methods=['POST'])
def create():
    """创建订单"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    form        = request.form
    carts_id    = form.get('carts_id', '[]').strip()
    ua_id       = toint(form.get('ua_id', '0'))
    shipping_id = toint(form.get('shipping_id', '0'))
    coupon_id   = toint(form.get('coupon_id', '0'))

    try:
        carts_id = json.loads(carts_id)
    except Exception as e:
        return resjson.print_json(resjson.PARAM_ERROR)

    ocs = OrderCreateService(uid, carts_id, ua_id, shipping_id, coupon_id)
    if not ocs.check():
        return resjson.print_json(11, ocs.msg)

    ocs.create()

    return resjson.print_json(0, u'ok', {'order':ocs.order})


@order.route('/update', methods=['POST'])
def update():
    """更新订单"""
    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    form        = request.form
    order_id    = toint(form.get('order_id', '0'))
    ua_id       = toint(form.get('ua_id', '0'))
    shipping_id = toint(form.get('shipping_id', '0'))
    coupon_id   = toint(form.get('coupon_id', '0'))

    ous = OrderUpdateService(uid, order_id, ua_id, shipping_id, coupon_id)
    if not ous.check():
        return resjson.print_json(11, ous.msg)

    ous.update()

    return resjson.print_json(0, u'ok')


@order.route('/cancel')
def cancel():
    """取消订单"""
    resjson.action_code = 12

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    args        = request.args
    order_id    = toint(args.get('order_id', 0))
    cancel_desc = args.get('cancel_desc', '').strip()

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    ocs = OrderCancelService(order_id, uid, cancel_desc)

    if not ocs.check():
        return resjson.print_json(10, ocs.msg)

    ocs.cancel()
    ocs.commit()

    return resjson.print_json(0, u'ok')


@order.route('/deliver')
def deliver():
    """确认收货"""
    resjson.action_code = 13

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    args     = request.args
    order_id = toint(args.get('order_id', 0))

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)
    
    ods = OrderDeliverService(order_id, uid)
    if not ods.check():
        return resjson.print_json(10, ods.msg)

    ods.deliver()
    ods.commit()

    return resjson.print_json(0, u'ok')


@order.route('/remove')
def remove():
    """软删除订单"""
    resjson.action_code = 14

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    order_id = toint(request.args.get('order_id', 0))

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()

    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.order_status not in (2,3):
        return resjson.print_json(11, _(u'当前订单状态不允许删除订单'))

    model_update(order, {'is_remove':1}, commit=True)

    return resjson.print_json(0, u'ok')


@order.route('/save-comment', methods=["POST"])
def save_comment():
    """评价订单商品"""
    resjson.action_code = 15

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid      = get_uid()
    nickname = get_nickname()
    avatar   = get_avatar()

    wtf_form     = CommentOrderGoodsForm()
    current_time = current_timestamp()

    if not wtf_form.validate_on_submit():
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    oa_id       = wtf_form.oa_id.data
    order_goods = OrderGoods.query.get(oa_id)
    if not order_goods:
        return resjson.print_json(12, _(u'订单商品不存在'))
    
    order = Order.query.filter(Order.order_id == order_goods.order_id).filter(Order.uid == uid).first()
    if not order:
        return resjson.print_json(13, _(u'订单商品不存在'))

    img_data = wtf_form.img_data.data
    img_data = img_data.split(',')

    # 检测图片合法性 ??

    img_data = json.dumps(img_data) if len(img_data) > 0 else '[]'

    data = {'uid':uid, 'nickname':nickname, 'avatar':avatar, 'ttype':1, 'tid':order_goods.goods_id,
            'rating':wtf_form.rating.data, 'content':wtf_form.content.data, 'img_data':img_data, 'add_time':current_time}
    model_create(Comment, data, commit=True)

    return resjson.print_json(0, u'ok')