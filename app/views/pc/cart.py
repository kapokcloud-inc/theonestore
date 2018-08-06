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
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_session_id
)

from app.services.api.cart import (
    CartService,
    CheckoutService,
    CartStaticMethodsService
)


cart = Blueprint('pc.cart', __name__)

@cart.route('/')
def root():
    """pc - 我的购物车"""

    uid        = get_uid()
    session_id = get_session_id()

    msg = request.args.get('msg', '').strip()

    cs = CartService(uid, session_id)
    cs.check()

    data = {'msg':msg, 'carts':cs.carts, 'items_amount':cs.items_amount, 'items_quantity':cs.items_quantity,
            'cart_total':cs.cart_total, 'cart_valid_total':cs.cart_valid_total}
    return render_template('pc/cart/index.html.j2', **data)


@cart.route('/checkout')
def checkout():
    """确认订单"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    # 结算页面
    ret, msg, data, url = CartStaticMethodsService.checkout_page(uid, 'pc')
    if not ret:
        return redirect(url)

    return render_template('pc/cart/checkout.html.j2', **data)


@cart.route('/pay')
def pay():
    """支付订单"""
    return render_template('pc/cart/pay.html.j2')
