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

from app.helpers import render_template
from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_session_id
)

from app.services.api.cart import CartService, CheckoutService

from app.forms.api.me import AddressForm

from app.models.item import Goods
from app.models.coupon import Coupon
from app.models.shipping import Shipping
from app.models.user import UserAddress
from app.models.cart import Cart

cart = Blueprint('mobile.cart', __name__)


@cart.route('/')
def root():
    """手机站 - 我的购物车"""

    uid        = get_uid()
    session_id = get_session_id()

    cs = CartService(uid, session_id)
    cs.check()

    return render_template('mobile/cart/index.html.j2', carts=cs.carts,
        items_amount=cs.items_amount, items_quantity=cs.items_quantity, total_quantity=cs.total_quantity)


@cart.route('/edit/<int:cart_id>')
def edit(cart_id):
    """手机站 - 购物车编辑"""

    uid        = get_uid()
    session_id = get_session_id()

    q = Cart.query.filter(Cart.cart_id == cart_id)

    if uid:
        q = q.filter(Cart.uid == uid)
    else:
        q = q.filter(Cart.session_id == session_id)

    cart = q.first()

    item = None
    if cart:
        item = Goods.query.get(cart.goods_id)

    return render_template('mobile/cart/cart_edit.html.j2', cart=cart, item=item)


@cart.route('/checkout')
def checkout():
    """结算"""

    #if not check_login():
    #    session['weixin_login_url'] = request.headers['Referer']
    #    return redirect(url_for('api.weixin.login'))
    #uid = get_uid()
    uid = 1
    current_time = current_timestamp()

    carts    = db.session.query(Cart.cart_id).filter(Cart.uid == uid).filter(Cart.is_checked).all()
    carts_id = [cart.cart_id for cart in carts]

    # 快递列表
    _shipping_list = Shipping.query.\
                        filter(Shipping.is_enable == 1).\
                        order_by(Shipping.sorting.desc(), Shipping.shipping_amount.asc()).all()
    if len(_shipping_list) <= 0:
        return render_template('mobile/cart/checkout.html.j2', msg=_(u'系统末配置快递'))

    # 默认快递
    default_shipping = Shipping.query.filter(Shipping.is_enable == 1).filter(Shipping.is_default == 1).first()
    default_shipping = default_shipping if default_shipping else _shipping_list[0]

    cs = CheckoutService(uid, carts_id, default_shipping.shipping_id)
    if not cs.check():
        return render_template('mobile/cart/checkout.html.j2', msg=cs.msg)

    # 收货地址
    addresses       = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.is_default.desc()).all()
    default_address = UserAddress.query.filter(UserAddress.uid == uid).filter(UserAddress.is_default == 1).first()
    if not default_address:
        default_address = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.ua_id.desc()).first()

    # 优惠券
    coupons = Coupon.query.\
                filter(Coupon.uid == uid).\
                filter(Coupon.is_valid == 1).\
                filter(Coupon.begin_time <= current_time).\
                filter(Coupon.end_time >= current_time).\
                order_by(Coupon.coupon_id.desc()).all()

    # 快递
    shipping_list  = []
    for _s in _shipping_list:
        titel    = _(u'%s  ￥%s(满￥%s免运费)' % (_s.shipping_name, _s.shipping_amount, _s.free_limit_amount))
        shipping = u'{"title":"%s", "value":%s}' % (titel, _s.shipping_id)
        shipping_list.append(shipping)
    shipping_list  = ','.join(shipping_list)
    shipping_list  = '[%s]' % shipping_list
    shipping_title = _(u'%s  ￥%s(满￥%s免运费)' %\
                        (default_shipping.shipping_name, default_shipping.shipping_amount, default_shipping.free_limit_amount))

    wtf_form = AddressForm()

    data = {'carts':cs.carts, 'items_amount':cs.items_amount, 'shipping_amount':cs.shipping_amount,
            'discount_amount':cs.discount_amount, 'pay_amount':cs.pay_amount,
            'addresses':addresses, 'default_address':default_address,
            'shipping_list':shipping_list, 'default_shipping':default_shipping, 'shipping_title':shipping_title,
            'coupons':coupons, 'wtf_form':wtf_form}

    return render_template('mobile/cart/checkout.html.j2', **data)
