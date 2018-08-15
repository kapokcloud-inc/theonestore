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
    model_create,
    model_update,
    model_delete,
    log_info,
    toint,
    url_push_query
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_session_id
)

from app.services.api.cart import (
    CartService,
    CartStaticMethodsService
)

from app.models.item import Goods
from app.models.cart import Cart


cart = Blueprint('mobile.cart', __name__)

@cart.route('/')
def root():
    """手机站 - 我的购物车"""

    uid        = get_uid()
    session_id = get_session_id()

    msg = request.args.get('msg', '').strip()

    cs = CartService(uid, session_id)
    cs.check()

    data = {'msg':msg, 'carts':cs.carts, 'items_amount':cs.items_amount, 'items_quantity':cs.items_quantity,
            'cart_valid_total':cs.cart_valid_total}
    return render_template('mobile/cart/index.html.j2', **data)


@cart.route('/edit/<int:cart_id>')
def edit(cart_id):
    """手机站 - 购物车编辑"""

    uid        = get_uid()
    session_id = get_session_id()

    q = Cart.query.filter(Cart.cart_id == cart_id).filter(Cart.checkout_type == 1)

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

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args     = request.args
    order_id = toint(args.get('order_id', '0'))

    # 订单付款页面
    if order_id > 0:
        ret, msg, data, url = CartStaticMethodsService.pay_page(order_id, uid, 'mobile')
        if not ret:
            return redirect(url)

        data['openid'] = session.get('jsapi_weixin_openid', '')
        return render_template('mobile/cart/pay.html.j2', **data)

    # 结算页面
    ret, msg, data, url = CartStaticMethodsService.checkout_page(uid, 'mobile')
    if not ret:
        return redirect(url)

    return render_template('mobile/cart/checkout.html.j2', **data)
