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

from app.forms.api.order import OrderAddressForm

from app.exception import (
    TheonestoreException,
    OrderException,
    ShippingException
)
from app.services.response import ResponseJson
from app.services.track import TrackServiceFactory
from app.services.message import MessageCreateService
from app.services.api.pay_weixin import NativeService
from app.services.api.order import (
    OrderStaticMethodsService,
    OrderService,
    OrderUpdateService,
    OrderCancelService,
    OrderDeliverService,
    RechargeOrderCreateService,
    PayService
)
from app.forms.api.comment import CommentOrderGoodsForm

from app.models.item import Goods
from app.models.comment import Comment
from app.models.shipping import Shipping
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods
)


order = Blueprint('api.order', __name__)

resjson = ResponseJson()
resjson.module_code = 14


@order.route('/index', methods=['GET'])
def index():
    """订单列表页"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    data = OrderStaticMethodsService.orders(uid, request.args.to_dict())
    data['tab_status'] = request.args.get('tab_status', '0')

    return resjson.print_json(0, u'ok', data)


@order.route('/detail')
def detail():
    """订单详情"""

    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    order_id = toint(request.args.get('order_id', '0'))

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    data = OrderStaticMethodsService.detail_page(order_id, uid)

    return resjson.print_json(0, u'ok', data)


@order.route('/create', methods=['POST'])
def create():
    """创建订单"""
    resjson.action_code = 12

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    form = request.form
    carts_id = form.get('carts_id', '[]').strip()
    ua_id = toint(form.get('ua_id', '0'))
    shipping_id = toint(form.get('shipping_id', '0'))
    coupon_id = toint(form.get('coupon_id', '0'))
    log_info(form)

    try:
        carts_id = json.loads(carts_id)
    except Exception as e:
        return resjson.print_json(resjson.PARAM_ERROR)

    try:
        order_service = OrderService(
            uid,
            1,
            user_address_id=ua_id,
            cart_id_list=carts_id,
            coupon_id=coupon_id,
            shipping_id=shipping_id)
        orderinfo = order_service.create()
    except TheonestoreException as e:
        resjson.print_json(30, e.msg)
    return resjson.print_json(0, u'ok', {'order_id': orderinfo.order_id})


@order.route('/update', methods=['POST'])
def update():
    """更新订单"""
    resjson.action_code = 13

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    form = request.form
    order_id = toint(form.get('order_id', '0'))
    ua_id = toint(form.get('ua_id', '0'))
    shipping_id = toint(form.get('shipping_id', '0'))
    coupon_id = toint(form.get('coupon_id', '0'))

    ous = OrderUpdateService(uid, order_id, ua_id, shipping_id, coupon_id)
    try:
        ous.update()
    except OrderException as e:
        msg = u"%s" % e.msg
        return resjson.print_json(11, msg)
    ous.update()

    return resjson.print_json(0, u'ok')


@order.route('/cancel')
def cancel():
    """取消订单"""
    resjson.action_code = 14

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))
    cancel_desc = args.get('cancel_desc', '').strip()

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    ocs = OrderCancelService(order_id, uid, cancel_desc)
    try:
        ocs.cancel()
    except OrderException as e:
        msg = u'%s' % e.msg
        return resjson.print_json(11, msg)

    return resjson.print_json(0, u'ok')


@order.route('/deliver')
def deliver():
    """确认收货"""
    resjson.action_code = 15

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    ods = OrderDeliverService(order_id, uid)
    try:
        ods.deliver()
    except OrderException as e:
        msg = u'%s' % e.msg
        return resjson.print_json(10, msg)

    return resjson.print_json(0, u'ok')


@order.route('/remove')
def remove():
    """ 删除订单 """
    resjson.action_code = 16

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    order_id = toint(request.args.get('order_id', 0))

    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    order = Order.query.filter(Order.order_id == order_id).filter(
        Order.uid == uid).first()

    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.order_status not in (2, 3):
        return resjson.print_json(11, _(u'当前订单状态不允许删除订单'))

    model_update(order, {'is_remove': 1}, commit=True)

    return resjson.print_json(0, u'ok')


@order.route('/save-comment', methods=["POST"])
def save_comment():
    """评价订单商品"""
    resjson.action_code = 17

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()
    nickname = get_nickname()
    avatar = get_avatar()

    wtf_form = CommentOrderGoodsForm()
    current_time = current_timestamp()

    if not wtf_form.validate_on_submit():
        for key, value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    og_id = wtf_form.og_id.data
    order_goods = OrderGoods.query.get(og_id)
    if not order_goods:
        return resjson.print_json(12, _(u'订单商品不存在'))

    order = Order.query.filter(Order.order_id == order_goods.order_id).filter(
        Order.uid == uid).first()
    if not order:
        return resjson.print_json(13, _(u'订单商品不存在'))

    data = {'uid': uid, 'nickname': nickname, 'avatar': avatar, 'ttype': 1, 'tid': order_goods.goods_id,
            'rating': wtf_form.rating.data, 'content': wtf_form.content.data,
            'img_data': wtf_form.img_data.data, 'add_time': current_time}
    comment = model_create(Comment, data, commit=True)

    item = Goods.query.get(order_goods.goods_id)
    if item:
        comment_count = Comment.query.\
            filter(Comment.ttype == 1).\
            filter(Comment.tid == order_goods.goods_id).count()
        good_count = Comment.query.\
            filter(Comment.ttype == 1).\
            filter(Comment.tid == order_goods.goods_id).\
            filter(Comment.rating == 3).count()
        comment_good_rate = round(
            (Decimal(good_count)/Decimal(comment_count)) * 100)
        model_update(item, {'comment_count': comment_count,
                            'comment_good_rate': comment_good_rate})

    model_update(order_goods, {'comment_id': comment.comment_id}, commit=True)

    # 站内消息
    content = _(u'您已评价“%s”。' % order_goods.goods_name)
    mcs = MessageCreateService(
        1, uid, -1, content, ttype=2, tid=og_id, current_time=current_time)
    if not mcs.check():
        log_error('[ErrorViewApiOrderSaveComment][MessageCreateError]  og_id:%s msg:%s' % (
            og_id, mcs.msg))
    else:
        mcs.do()

    return resjson.print_json(0, u'ok')


@order.route('/recharge', methods=['POST'])
def recharge():
    """创建充值订单"""
    resjson.action_code = 18

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    form = request.form
    recharge_amount = form.get('recharge_amount', '0.00').strip()
    is_qrcode = toint(form.get('is_qrcode', '0'))

    rocs = RechargeOrderCreateService(uid, recharge_amount)
    if not rocs.check():
        return resjson.print_json(11, rocs.msg)

    rocs.create()

    qrcode = ''
    if is_qrcode == 1:
        # 创建支付
        ps = PayService(uid, [rocs.order.order_id])
        if not ps.check():
            return resjson.print_json(12, ps.msg)

        if not ps.tran:
            ps.create_tran()

        tran = ps.tran
        tran_id = tran.tran_id
        subject = u'交易号：%d' % tran_id
        nonce_str = str(tran_id)
        pay_amount = Decimal(tran.pay_amount).quantize(Decimal('0.00'))*100

        # 支付二维码
        ns = NativeService(nonce_str, subject, tran_id,
                           pay_amount, request.remote_addr)
        if not ns.create_qrcode():
            return resjson.print_json(13, ns.msg)
        qrcode = ns.qrcode

    return resjson.print_json(0, u'ok', {'order_id': rocs.order.order_id, 'qrcode': qrcode})


@order.route('/is-paid')
def is_paid():
    """查询订单是否支付成功"""
    resjson.action_code = 19

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    order_id = toint(request.args.get('order_id', '0'))
    order = Order.query.filter(Order.order_id == order_id).filter(
        Order.uid == uid).first()
    if order and order.pay_status == 2:
        return resjson.print_json(0, u'ok', {'is_paid': 1})

    return resjson.print_json(0, u'ok', {'is_paid': 0})


@order.route('/update-address', methods=["POST"])
def update_address():
    """更新订单收货地址"""
    resjson.action_code = 20

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    wtf_form = OrderAddressForm()
    current_time = current_timestamp()

    if not wtf_form.validate_on_submit():
        for key, value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    order_address = OrderAddress.query.get(wtf_form.oa_id.data)
    if not order_address:
        return resjson.print_json(12, _(u'订单地址不存在'))

    order = Order.query.\
        filter(Order.order_id == order_address.order_id).\
        filter(Order.uid == uid).first()
    if not order:
        return resjson.print_json(13, _(u'订单不存在'))

    if order.pay_status != 1:
        return resjson.print_json(14, _(u'未付款订单才可以修改地址'))

    data = {'name': wtf_form.name.data, 'mobile': wtf_form.mobile.data,
            'province': wtf_form.province.data, 'city': wtf_form.city.data,
            'district': wtf_form.district.data, 'address': wtf_form.address.data,
            'update_time': current_time}
    model_update(order_address, data, commit=True)

    return resjson.print_json(0, u'ok')


@order.route('/comment')
def comment():
    """ 评价中心 """
    resjson.action_code = 21

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    params = request.args.to_dict()

    p = toint(params.get('p', '1'))
    ps = toint(params.get('ps', '10'))
    is_pending = toint(params.get('is_pending', '0'))

    if p <= 0 or ps <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    if is_pending not in [0, 1]:
        return resjson.print_json(resjson.PARAM_ERROR)

    data_temp = OrderStaticMethodsService.order_comments(uid, params, True)

    data = {'is_pending': data_temp['is_pending'], 'pending_count': data_temp['pending_count'],
            'unpending_count': data_temp['unpending_count'], 'comments': data_temp['comments']}

    return resjson.print_json(0, u'ok', data)


@order.route('/comment/detail')
def comment_detail():
    """手机站 - 查看评价"""

    resjson.action_code = 22

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    og_id = toint(request.args.get('og_id', '0'))

    if og_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    order_goods = OrderGoods.query.get(og_id)
    good = Goods.query.get(order_goods.goods_id)
    comment = Comment.query.filter(
        Comment.comment_id == order_goods.comment_id).filter(Comment.uid == uid).first()
    if not comment:
        return resjson.print_json(10, u'评价不存在')
    data = {'order_goods': order_goods, 'comment': comment, 'good': good}
    return resjson.print_json(0, u'ok', data)


@order.route('/track')
def track():
    """查询物流"""
    resjson.action_code = 23

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))
    if order_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    order = Order.query.filter(Order.order_id == order_id).filter(
        Order.uid == uid).first()
    if not order:
        return resjson.print_json(10, u'订单不存在')

    order_address = OrderAddress.query.\
        filter(OrderAddress.order_id == order_id).first()

    shipping = None
    express_msg = ''
    express_data = []
    if order and order.shipping_status == 2:
        try:
            trackservice = TrackServiceFactory.get_trackservice()
            _express_data = trackservice.track(
                order.shipping_id,
                order.shipping_sn,
                order_address.mobile)
            express_data = _express_data
            shipping = trackservice.shipping
            express_msg = 'ok'
        except ShippingException as e:
            express_msg = e.msg

    data = {
        'express_msg': express_msg,
        'express_data': express_data,
        'order': order,
        'shipping': shipping}
    return resjson.print_json(0, u'ok', data)
