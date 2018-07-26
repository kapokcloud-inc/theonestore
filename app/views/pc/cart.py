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
    CheckoutService
)

from app.forms.api.me import AddressForm

from app.models.order import (
    Order,
    OrderAddress
)
from app.models.funds import Funds
from app.models.item import Goods
from app.models.coupon import Coupon
from app.models.shipping import Shipping
from app.models.user import UserAddress
from app.models.cart import Cart


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
            'total_quantity':cs.total_quantity}
    return render_template('pc/cart/index.html.j2', **data)


@cart.route('/checkout')
def checkout():
    """pc - 结算"""

    # if not check_login():
    #     session['weixin_login_url'] = request.headers['Referer']
    #     return redirect(url_for('api.weixin.login'))
    # uid = get_uid()

    # args         = request.args
    # order_id     = args.get('order_id', None)
    # current_time = current_timestamp()

    # # 钱包
    # funds = Funds.query.filter(Funds.uid == uid).first()

    # # 订单付款
    # if order_id is not None:
    #     order_id = toint(order_id)

    #     # 检查
    #     if order_id <= 0:
    #         return redirect(request.headers['Referer'])

    #     # 检查
    #     order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
    #     if not order:
    #         return redirect(request.headers['Referer'])
        
    #     order_address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()
    #     coupon        = Coupon.query.filter(Coupon.order_id == order_id).first()

    #     shipping_title = _(u'%s  ￥%s(满￥%s免运费)' % (order.shipping_name, order.shipping_amount, order.free_limit_amount))

    #     data = {'order':order, 'order_address':order_address, 'coupon':coupon,
    #             'shipping_title':shipping_title, 'funds':funds.funds}
    #     return render_template('pc/cart/pay.html.j2', **data)

    # # 立即购买或结算
    # buy_now = toint(args.get('buy_now', '0'))
    # if buy_now == 1:
    #     goods_id = toint(args.get('goods_id', '0'))

    #     # 检查
    #     if goods_id <= 0:
    #         return redirect(request.headers['Referer'])

    #     # 检查
    #     goods = Goods.query.get(goods_id)
    #     if not goods:
    #         return redirect(request.headers['Referer'])

    #     # 删除
    #     _cart = Cart.query.\
    #                     filter(Cart.uid == uid).\
    #                     filter(Cart.goods_id == goods_id).\
    #                     filter(Cart.checkout_type == 2).first()
    #     if _cart:
    #         model_delete(_cart, commit=True)

    #     data = {'uid':uid, 'goods_id':goods_id, 'quantity':1, 'is_checked':1, 'checkout_type':2,
    #             'add_time':current_time, 'update_time':current_time}
    #     cart = model_create(Cart, data, commit=True)

    #     carts_id = [cart.cart_id]
    # else:
    #     carts_id = args.get('carts_id', '[]').strip()
    #     try:
    #         carts_id = json.loads(carts_id)
    #         carts_id = [toint(cart_id) for cart_id in carts_id]
    #     except Exception as e:
    #         return redirect(url_for('pc.cart.root', msg=_(u'系统错误:参数错误')))

    # # 快递列表
    # _shipping_list = Shipping.query.\
    #                     filter(Shipping.is_enable == 1).\
    #                     order_by(Shipping.sorting.desc(), Shipping.shipping_amount.asc()).all()
    # if len(_shipping_list) <= 0:
    #     return redirect(url_for('pc.cart.root', msg=_(u'系统末配置快递')))

    # # 默认快递
    # default_shipping = Shipping.query.filter(Shipping.is_enable == 1).filter(Shipping.is_default == 1).first()
    # default_shipping = default_shipping if default_shipping else _shipping_list[0]

    # cs = CheckoutService(uid, carts_id, default_shipping.shipping_id)
    # if not cs.check():
    #     return redirect(url_for('pc.cart.root', msg=cs.msg))

    # # 收货地址
    # addresses       = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.is_default.desc()).all()
    # default_address = UserAddress.query.filter(UserAddress.uid == uid).filter(UserAddress.is_default == 1).first()
    # if not default_address:
    #     default_address = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.ua_id.desc()).first()

    # # 优惠券
    # coupons = Coupon.query.\
    #             filter(Coupon.uid == uid).\
    #             filter(Coupon.is_valid == 1).\
    #             filter(Coupon.begin_time <= current_time).\
    #             filter(Coupon.end_time >= current_time).\
    #             order_by(Coupon.coupon_id.desc()).all()

    # # 快递
    # shipping_list  = []
    # for _s in _shipping_list:
    #     titel    = _(u'%s  ￥%s(满￥%s免运费)' % (_s.shipping_name, _s.shipping_amount, _s.free_limit_amount))
    #     shipping = u'{"title":"%s", "value":%s}' % (titel, _s.shipping_id)
    #     shipping_list.append(shipping)
    # shipping_list  = ','.join(shipping_list)
    # shipping_list  = '[%s]' % shipping_list
    # shipping_title = _(u'%s  ￥%s(满￥%s免运费)' %\
    #                     (default_shipping.shipping_name, default_shipping.shipping_amount, default_shipping.free_limit_amount))

    # wtf_form = AddressForm()
    # carts_id = [cart_id.__str__() for cart_id in carts_id]
    # carts_id = ','.join(carts_id)

    # data = {'carts':cs.carts, 'carts_id':carts_id, 'items_amount':cs.items_amount,
    #         'shipping_amount':cs.shipping_amount, 'discount_amount':cs.discount_amount, 'pay_amount':cs.pay_amount,
    #         'addresses':addresses, 'default_address':default_address,
    #         'shipping_list':shipping_list, 'default_shipping':default_shipping, 'shipping_title':shipping_title,
    #         'coupons':coupons, 'funds':funds.funds, 'wtf_form':wtf_form}

    # return render_template('pc/cart/checkout.html.j2', **data)
    return render_template('pc/cart/checkout.html.j2')
