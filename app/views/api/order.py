# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
from decimal import Decimal

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
    log_error,
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
from app.services.message import MessageCreateService
from app.services.api.order import (
    OrderCreateService,
    OrderUpdateService,
    OrderCancelService,
    OrderDeliverService,
    RechargeOrderCreateService
)

from app.forms.api.comment import CommentOrderGoodsForm

from app.models.item import Goods
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

    return resjson.print_json(0, u'ok', {'order_id':ocs.order.order_id})


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

    og_id       = wtf_form.og_id.data
    order_goods = OrderGoods.query.get(og_id)
    if not order_goods:
        return resjson.print_json(12, _(u'订单商品不存在'))
    
    order = Order.query.filter(Order.order_id == order_goods.order_id).filter(Order.uid == uid).first()
    if not order:
        return resjson.print_json(13, _(u'订单商品不存在'))

    data = {'uid':uid, 'nickname':nickname, 'avatar':avatar, 'ttype':1, 'tid':order_goods.goods_id,
            'rating':wtf_form.rating.data, 'content':wtf_form.content.data,
            'img_data':wtf_form.img_data.data, 'add_time':current_time}
    comment = model_create(Comment, data, commit=True)

    item = Goods.query.get(order_goods.goods_id)
    if item:
        comment_count     = Comment.query.\
                                filter(Comment.ttype == 1).\
                                filter(Comment.tid == order_goods.goods_id).count()
        good_count        = Comment.query.\
                                filter(Comment.ttype == 1).\
                                filter(Comment.tid == order_goods.goods_id).\
                                filter(Comment.rating == 5).count()
        comment_good_rate = round((Decimal(good_count)/Decimal(good_count)) * 100)
        model_update(item, {'comment_count':comment_count, 'comment_good_rate':comment_good_rate})

    model_update(order_goods, {'comment_id':comment.comment_id}, commit=True)

    # 站内消息
    content = _(u'您已评价“%s”。' % order_goods.goods_name)
    mcs = MessageCreateService(1, uid, -1, content, ttype=2, tid=og_id, current_time=current_time)
    if not mcs.check():
        log_error('[ErrorViewApiOrderSaveComment][MessageCreateError]  og_id:%s msg:%s' % (og_id, mcs.msg))
    else:
        mcs.do()

    return resjson.print_json(0, u'ok')


@order.route('/recharge', methods=['POST'])
def recharge():
    """创建充值订单"""
    resjson.action_code = 16

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    form            = request.form
    recharge_amount = form.get('recharge_amount', '0.00').strip()

    rocs = RechargeOrderCreateService(uid, recharge_amount)
    if not rocs.check():
        return resjson.print_json(11, rocs.msg)

    rocs.create()

    return resjson.print_json(0, u'ok', {'order_id':rocs.order.order_id})
