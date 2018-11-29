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
    request,
    session
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    model_create,
    model_update,
    model_delete,
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.response import ResponseJson
from app.services.api.cart import (
    CartService,
    CheckoutService,
    CartStaticMethodsService
)

from app.models.order import (
    Order,
    OrderGoods
)
from app.models.item import Goods
from app.models.cart import Cart


cart = Blueprint('api.cart', __name__)

resjson = ResponseJson()
resjson.module_code = 12

@cart.route('/')
def index():
    """购物车"""
    resjson.action_code = 10

    uid        = get_uid()
    session_id = session.sid
    is_login   = 1 if uid else 0

    cs = CartService(uid, session_id)
    cs.check()
    log_info(cs)
    data = {'is_login':is_login, 'carts':cs.carts, 'cart_total':cs.cart_total,
            'cart_amount':cs.cart_amount, 'items_amount':cs.items_amount, 'items_quantity':cs.items_quantity}
    return resjson.print_json(0, u'ok', data)


@cart.route('/add')
def add():
    """加入购物车"""
    resjson.action_code = 11

    uid        = get_uid()
    session_id = session.sid

    args         = request.args
    order_id     = toint(args.get('order_id', '0'))
    goods_id     = toint(args.get('goods_id', '0'))
    quantity     = toint(args.get('quantity', '1'))
    current_time = current_timestamp()
    items_data   = []

    if order_id > 0:
        order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
        if not order:
            return resjson.print_json(resjson.PARAM_ERROR)
        
        order_goods = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
        for _order_goods in order_goods:
            items_data.append({'goods_id':_order_goods.goods_id, 'quantity':_order_goods.goods_quantity})
    else:
        # 检查
        if goods_id <= 0 or quantity < 1:
            return resjson.print_json(resjson.PARAM_ERROR)
        
        items_data.append({'goods_id':goods_id, 'quantity':quantity})

    for item_data in items_data:
        goods_id = item_data.get('goods_id')
        quantity = item_data.get('quantity')

        # 检查
        item = Goods.query.get(goods_id)
        if not item:
            return resjson.print_json(10, _(u'找不到商品'))

        # 获取购物车商品
        q = Cart.query.filter(Cart.goods_id == goods_id).filter(Cart.checkout_type == 1)
        if uid:
            q = q.filter(Cart.uid == uid)
        else:
            q = q.filter(Cart.session_id == session_id)
        cart = q.first()

        # 是否创建购物车商品
        if not cart:
            data = {'uid':uid, 'session_id':session_id, 'goods_id':goods_id, 'quantity':0,
                    'is_checked':1, 'checkout_type':1, 'add_time':current_time}
            cart = model_create(Cart, data)

        # 更新购物车商品
        quantity += cart.quantity
        data      = {'quantity':quantity, 'update_time':current_time}
        cart = model_update(cart, data)

    db.session.commit()

    cs = CartService(uid, session_id)
    cs.check()
    session['cart_total'] = cs.cart_total

    return resjson.print_json(0, u'ok', {'cart_total':cs.cart_total})


@cart.route('/update')
def update():
    """更新购物车"""
    resjson.action_code = 12

    uid        = get_uid()
    session_id = session.sid

    args         = request.args
    cart_id      = toint(args.get('cart_id', 0))
    quantity     = toint(args.get('quantity', 0))
    current_time = current_timestamp()

    # 检查
    if cart_id <= 0 or quantity <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    # 获取购物车商品
    q = Cart.query.filter(Cart.cart_id == cart_id).filter(Cart.checkout_type == 1)
    if uid:
        q = q.filter(Cart.uid == uid)
    else:
        q = q.filter(Cart.session_id == session_id)
    cart = q.first()
    if cart is None:
        return resjson.print_json(10, _(u'购物车里找不到商品'))

    # 更新购物车商品
    data = {'quantity':quantity, 'update_time':current_time}
    model_update(cart, data, commit=True)

    cs = CartService(uid, session_id)
    cs.check()
    session['cart_total'] = cs.cart_total

    for _cart in cs.carts:
        if _cart['cart'].cart_id == cart_id:
            _items_amount = _cart['items_amount']

    # 商品状态
    item = Goods.query.get(cart.goods_id)
    is_valid, valid_status = CartStaticMethodsService.check_item_statue(item, cart)

    data = {'cart_total':cs.cart_total, 'items_quantity':cs.items_quantity,
            'items_amount':cs.items_amount, '_items_amount':_items_amount,
            'is_valid':is_valid, 'valid_status':valid_status}
    return resjson.print_json(0, u'ok', data)


@cart.route('/remove')
def remove():
    """删除购物车商品"""
    resjson.action_code = 13

    uid        = get_uid()
    session_id = session.sid

    carts_id = request.args.get('carts_id', '').strip()
    carts_id = carts_id.split(',')

    # 检查
    if len(carts_id) == 0:
        return resjson.print_json(10, _(u'请选择需要删除的商品'))

    for cart_id in carts_id:
        # 获取购物车商品
        q = Cart.query.filter(Cart.cart_id == cart_id).filter(Cart.checkout_type == 1)
        if uid:
            q = q.filter(Cart.uid == uid)
        else:
            q = q.filter(Cart.session_id == session_id)
        cart = q.first()
        if cart is None:
            return resjson.print_json(11, _(u'购物车里找不到商品'))

        # 删除购物车商品
        model_delete(cart)

    db.session.commit()

    cs = CartService(uid, session_id)
    cs.check()
    session['cart_total'] = cs.cart_total

    data = {'cart_total':cs.cart_total, 'items_quantity':cs.items_quantity,
            'items_amount':cs.items_amount}
    return resjson.print_json(0, u'ok', data)


@cart.route('/checked')
def checked():
    """选中"""
    resjson.action_code = 14

    uid        = get_uid()
    session_id = session.sid

    carts        = request.args.get('carts', '[]').strip()
    current_time = current_timestamp()

    try:
        carts = json.loads(carts)
    except Exception as e:
        return resjson.print_json(resjson.PARAM_ERROR)
    for cart in carts:
        cart_id    = toint(cart.get('cart_id', 0))
        is_checked = toint(cart.get('is_checked', -1))

        # 检查
        if cart_id <= 0 or is_checked not in [0,1]:
            return resjson.print_json(resjson.PARAM_ERROR)

        # 获取购物车商品
        q = Cart.query.filter(Cart.cart_id == cart_id).filter(Cart.checkout_type == 1)
        if uid:
            q = q.filter(Cart.uid == uid)
        else:
            q = q.filter(Cart.session_id == session_id)
        cart = q.first()
        if cart is None:
            return resjson.print_json(10, _(u'购物车里找不到商品'))

        # 更新购物车商品
        data = {'is_checked':is_checked, 'update_time':current_time}
        model_update(cart, data)

    db.session.commit()

    cs = CartService(uid, session_id)
    cs.check()

    data = {'cart_total':cs.cart_total, 'items_quantity':cs.items_quantity,
            'items_amount':cs.items_amount}
    return resjson.print_json(0, u'ok', data)


@cart.route('/checkout/amounts')
def checkout_amounts():
    """结算金额"""
    resjson.action_code = 15

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    carts_id    = args.get('carts_id', '[]').strip()
    shipping_id = toint(args.get('shipping_id', '0'))
    coupon_id   = toint(args.get('coupon_id', '0'))

    try:
        carts_id = json.loads(carts_id)
        carts_id = [toint(cart_id) for cart_id in carts_id]
    except Exception as e:
        return resjson.print_json(resjson.PARAM_ERROR)

    cs = CheckoutService(uid, carts_id, shipping_id, coupon_id)
    if not cs.check():
        return resjson.print_json(11, cs.msg)

    data = {'items_amount':cs.items_amount,
            'shipping_amount':cs.shipping_amount,
            'discount_amount':cs.discount_amount,
            'pay_amount':cs.pay_amount}
    return resjson.print_json(0, u'ok', data)


@cart.route('/checkout')
def checkout():
    """确认订单"""
    
    resjson.action_code = 16

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()
    
    args = request.args
    order_id = toint(args.get('order_id', 0))
    # 已有订单,获取订单数据
    if order_id > 0:
        data = CartStaticMethodsService.pay_page(order_id, uid, 'api')
        if not data[0]:
            return resjson.print_json(11, data[1])
            
        return resjson.print_json(0, u'ok', data[2])

    buy_now = toint(args.get('buy_now', 0))
    goods_id = toint(args.get('goods_id', 0))
    carts_id = args.get('carts_id', '')

    if buy_now not in [0, 1]:
        return resjson.print_json(resjson.PARAM_ERROR)
    # 立即购买
    if buy_now == 1 and goods_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)
    # 购物车购买
    if buy_now == 0 and carts_id == '':
        return resjson.print_json(resjson.PARAM_ERROR)

    # 结算页面
    data = CartStaticMethodsService.checkout_page(uid, 'api')
    if not data[0]:
        return resjson.print_json(11, data[1])

    return resjson.print_json(0, u'ok', data[2])