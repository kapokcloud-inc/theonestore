# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import base64
import json
import qrcode
from io import BytesIO

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

from app.services.api.order import PayService
from app.services.api.pay_weixin import UnifiedorderService
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
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    # 结算页面
    ret, msg, data, url = CartStaticMethodsService.checkout_page(uid, 'pc')
    if not ret:
        return redirect(url)

    return render_template('pc/cart/checkout.html.j2', **data)


@cart.route('/pay/<int:order_id>')
def pay(order_id):
    """支付订单"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    ret, msg, data, url = CartStaticMethodsService.pay_page(order_id, uid, 'pc')
    if not ret:
        return redirect(url)

    # 创建支付
    ps = PayService(uid, [order_id])
    if not ps.check():
        return redirect(url_for('pc.order.index', msg=ps.msg))

    if not ps.tran:
        ps.create_tran()

    tran      = ps.tran
    subject   = u'交易号：%d' % tran.tran_id
    nonce_str = str(tran.tran_id)

    # 统一下单
    us = UnifiedorderService(nonce_str, subject, tran.tran_id, tran.pay_amount*100,
                            'NATIVE', request.remote_addr)

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(us.code_url)
    qr.make(fit=True)
    img      = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    data['qrcode'] = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template('pc/cart/pay.html.j2', **data)
