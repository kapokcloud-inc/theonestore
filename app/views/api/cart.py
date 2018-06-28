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
    get_uid,
    get_session_id
)

from app.services.response import ResponseJson
from app.services.api.cart import CartService, CheckoutService

from app.models.item import Goods
from app.models.cart import Cart


cart = Blueprint('api.cart', __name__)

resjson = ResponseJson()
resjson.module_code = 12

@cart.route('/add')
def add():
    """加入购物车"""
    resjson.action_code = 10

    uid        = get_uid()
    session_id = get_session_id()

    args         = request.args
    goods_id     = toint(args.get('goods_id', 0))
    quantity     = toint(args.get('quantity', 1))
    current_time = current_timestamp()

    # 检查
    if goods_id <= 0 or quantity < 1:
        return resjson.print_json(resjson.PARAM_ERROR)

    # 检查
    goods = Goods.query.get(goods_id)
    if not goods:
        return resjson.print_json(10, _(u'找不到商品'))

    # 获取购物车商品
    q = Cart.query.filter(Cart.goods_id == goods_id)
    if uid:
        q = q.filter(Cart.uid == uid)
    else:
        q = q.filter(Cart.session_id == session_id)
    cart = q.first()

    # 是否创建购物车商品
    if not cart:
        data = {'uid':uid, 'session_id':session_id, 'goods_id':goods_id, 'quantity':0,
                'is_checked':1, 'add_time':current_time}
        cart = model_create(Cart, data)

    # 更新购物车商品
    quantity += cart.quantity
    data      = {'quantity':quantity, 'update_time':current_time}
    cart = model_update(cart, data)

    db.session.commit()

    return resjson.print_json(0, u'ok')


@cart.route('/update')
def update():
    """更新购物车"""
    resjson.action_code = 11

    uid        = get_uid()
    session_id = get_session_id()

    args         = request.args
    cart_id      = toint(args.get('cart_id', 0))
    quantity     = toint(args.get('quantity', 0))
    current_time = current_timestamp()

    # 检查
    if cart_id <= 0 or quantity <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    # 获取购物车商品
    q = Cart.query.filter(Cart.cart_id == cart_id)
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

    return resjson.print_json(0, u'ok')


@cart.route('/remove')
def remove():
    """删除购物车商品"""
    resjson.action_code = 12

    uid        = get_uid()
    session_id = get_session_id()

    carts_id = request.args.get('carts_id', '').strip()
    carts_id = carts_id.split(',')

    # 检查
    if len(carts_id) == 0:
        return resjson.print_json(10, _(u'请选择需要删除的商品'))

    for cart_id in carts_id:
        # 获取购物车商品
        q = Cart.query.filter(Cart.cart_id == cart_id)
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

    return resjson.print_json(0, u'ok')


@cart.route('/checked')
def checked():
    """选中"""
    resjson.action_code = 13

    uid        = get_uid()
    session_id = get_session_id()

    carts        = request.args.get('carts', '[]').strip()
    current_time = current_timestamp()

    try:
        carts = json.loads(carts)
    except Exception, e:
        return resjson.print_json(resjson.PARAM_ERROR)

    for cart in carts:
        cart_id    = toint(cart.get('cart_id', 0))
        is_checked = toint(cart.get('is_checked', -1))

        # 检查
        if cart_id <= 0 or is_checked not in [0,1]:
            return resjson.print_json(resjson.PARAM_ERROR)

        # 获取购物车商品
        q = Cart.query.filter(Cart.cart_id == cart_id)
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

    return resjson.print_json(0, u'ok', {'items_amount':cs.items_amount, 'items_quantity':cs.items_quantity})


@cart.route('/checkout/amounts')
def checkout_amounts():
    """结算金额"""
    resjson.action_code = 13

    #if not check_login():
    #    session['weixin_login_url'] = request.headers['Referer']
    #    return resjson.print_json(10, _(u'未登陆'))
    #uid = get_uid()
    uid = 1

    args = request.args
    shipping_id = toint(args.get('shipping_id', '0'))
    coupon_id   = toint(args.get('coupon_id', '0'))

    carts    = db.session.query(Cart.cart_id).filter(Cart.uid == uid).filter(Cart.is_checked).all()
    carts_id = [cart.cart_id for cart in carts]

    cs = CheckoutService(uid, carts_id, shipping_id, coupon_id)
    if not cs.check():
        return resjson.print_json(11, cs.msg)

    data = {'items_amount':cs.items_amount, 'shipping_amount':cs.shipping_amount,
            'discount_amount':cs.discount_amount, 'pay_amount':cs.pay_amount}
    return resjson.print_json(0, u'ok', data)
