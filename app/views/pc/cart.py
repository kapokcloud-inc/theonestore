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
    get_uid
)
from app.services.api.order import PayService
from app.services.api.pay_weixin import NativeService
from app.services.api.cart import (
    CartService,
    CheckoutService,
    CartStaticMethodsService
)
from app.models.item import Goods

cart = Blueprint('pc.cart', __name__)


@cart.route('/')
def root():
    """pc - 我的购物车"""

    uid = get_uid()
    session_id = session.sid

    msg = request.args.get('msg', '').strip()

    cs = CartService(uid, session_id)
    cs.check()

    data = {
        'msg': msg,
        'carts': cs.carts,
        'items_amount': cs.items_amount,
        'items_quantity': cs.items_quantity,
        'cart_total': cs.cart_total,
        'cart_valid_total': cs.cart_valid_total}
    return render_template('pc/cart/index.html.j2', **data)


@cart.route('/add')
def add():
    """购物车增加"""
    args = request.args
    goods_id = toint(args.get('goods_id', '0'))
    quantity = toint(args.get('quantity', '1'))
    goods = Goods.query.get_or_404(goods_id)
    goods_list = db.session.query(
        Goods.goods_id, Goods.goods_name, Goods.goods_img,
        Goods.goods_desc, Goods.goods_price, Goods.sale_count,
        Goods.fav_count, Goods.comment_count).\
        filter(Goods.cat_id == goods.cat_id).\
        filter(Goods.is_delete == 0).\
        filter(Goods.is_sale == 1).\
        filter(Goods.stock_quantity > 0).\
        filter(Goods.goods_id != goods_id).\
        order_by(Goods.sale_count.desc()).\
        order_by(Goods.fav_count.desc()).\
        order_by(Goods.goods_id.desc()).\
        limit(20).all()
    return render_template(
        'pc/cart/add.html.j2',
        goods=goods,
        goods_list=goods_list)


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

    ret, msg, data, url = CartStaticMethodsService.pay_page(
        order_id, uid, 'pc')
    if not ret:
        return redirect(url)

    # 创建支付
    ps = PayService(uid, [order_id])
    if not ps.check():
        return redirect(url_for('pc.order.index', msg=ps.msg))

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
        return redirect(url_for('pc.order.index', msg=ns.msg))
    data['qrcode'] = ns.qrcode

    return render_template('pc/cart/pay.html.j2', **data)
