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
    redirect,
    request,
    url_for
)
from flask_babel import gettext as _

from sqlalchemy import func

from app.database import db

from app.helpers import (
    log_info,
    toint,
    model_create,
    model_update,
    model_delete
)
from app.helpers.date_time import current_timestamp

from app.models.user import UserAddress
from app.models.funds import Funds
from app.models.order import (
    Order,
    OrderAddress
)
from app.models.shipping import Shipping
from app.models.coupon import Coupon
from app.models.item import Goods
from app.models.cart import Cart


class CartService(object):
    """购物车Service"""

    def __init__(self, uid, session_id):
        self.uid              = uid                 # 用户ID
        self.session_id       = session_id          # 用户session_id
        self.current_time     = current_timestamp() # 当前时间
        self.carts            = []                  # 购物车商品项
        self.items_amount     = Decimal('0.00')     # 选中商品项商品总价
        self.items_quantity   = 0                   # 选中商品项总件数
        self.cart_total       = 0                   # 商品项总件数
        self.cart_valid_total = 0                   # 商品项有效的总件数

    def check(self):
        """检查"""

        # 购物车商品项
        q = Cart.query.filter(Cart.checkout_type == 1)
        if self.uid:
            q = q.filter(Cart.uid == self.uid)
        else:
            q = q.filter(Cart.session_id == self.session_id)
        carts = q.order_by(Cart.cart_id.desc()).all()

        for cart in carts:
            is_valid     = 1    # 是否有效: 0.失效; 1.有效;
            valid_status = 0    # 失效状态: 0.默认; 1.下架; 2.缺货;

            # 检查 - 商品
            item = Goods.query.get(cart.goods_id)
            if not item:
                is_valid     = 0
                valid_status = 1

            # 检查 - 商品是否已经下架
            if item.is_sale != 1:
                is_valid     = 0
                valid_status = 1

            # 检查 - 商品是否库存不足
            if item.stock_quantity <= 0:
                is_valid     = 0
                valid_status = 2

            if is_valid == 1:
                if cart.is_checked == 1:
                    # 选中商品项商品总价
                    _items_amount = Decimal(item.goods_price) * cart.quantity
                    self.items_amount += _items_amount

                    # 选中商品项总件数
                    self.items_quantity += cart.quantity

                self.cart_valid_total += cart.quantity

            self.cart_total += cart.quantity

            items_amount = Decimal(item.goods_price) * cart.quantity

            self.carts.append({'cart':cart, 'item':item, 'is_valid':is_valid,
                                'valid_status':valid_status, 'items_amount':items_amount})

        return True


class CheckoutService(object):
    """结算Service"""

    def __init__(self, uid, carts_id, shipping_id, coupon_id=0):
        self.msg               = ''
        self.uid               = uid                    # 用户ID
        self.carts_id          = carts_id               # 购物车商品项ID列表
        self.shipping_id       = shipping_id            # 快递ID
        self.coupon_id         = coupon_id              # 优惠券ID
        self.current_time      = current_timestamp()
        self.coupon            = None                   # 优惠券实例
        self.shipping          = None                   # 快递实例
        self.carts             = []                     # 购物车商品项
        self.items_id          = []                     # 选中商品项商品ID列表
        self.items_amount      = Decimal('0.00')        # 选中商品项商品总价
        self.items_quantity    = 0                      # 选中商品项总件数
        self.shipping_amount   = Decimal('0.00')        # 快递金额
        self.coupon_amount     = Decimal('0.00')        # 优惠券金额
        self.discount_amount   = Decimal('0.00')        # 优惠金额
        self.pay_amount        = Decimal('0.00')        # 支付金额

    def check(self):
        """检查"""

        # 购物车全部商品项
        carts = Cart.query.filter(Cart.cart_id.in_(self.carts_id)).\
                        order_by(Cart.cart_id.desc()).all()

        # 检查
        if not carts:
            self.msg = _(u'请选择购物商品')
            return False

        for cart in carts:
            # 检查 - 是否用户的购物车商品项
            if cart.uid != self.uid:
                self.msg = _(u'非法的购物车商品项')
                return False
            
            # 检查 - 商品
            item = Goods.query.get(cart.goods_id)
            if not item:
                self.msg = _(u'商品不存在')
                return False

            # 检查 - 商品是否已经下架
            if item.is_sale != 1:
                self.msg = _(u'商品已经下架')
                return False

            # 检查 - 商品是否库存不足
            if item.stock_quantity <= 0:
                self.msg = _(u'商品库存不足')
                return False

            # 商品总金额
            _items_amount      = item.goods_price * cart.quantity
            self.items_amount += Decimal(_items_amount)

            self.items_id.append(item.goods_id)

            self.carts.append({'cart':cart, 'item':item})

            # 选中商品项总件数
            self.items_quantity += cart.quantity

        self.items_id = list(set(self.items_id))

        # 检查 - 快递
        self.shipping = Shipping.query.get(self.shipping_id)
        if not self.shipping:
            self.msg = _(u'快递不存在')
            return False

        # 快递金额: 不包邮或未满包邮金额
        if self.shipping.free_limit_amount == 0 or self.shipping.free_limit_amount > self.items_amount:
            self.shipping_amount = Decimal(self.shipping.shipping_amount)

        if self.coupon_id:
            # 检查 - 优惠券
            self.coupon = Coupon.query.filter(Coupon.coupon_id == self.coupon_id).filter(Coupon.uid == self.uid).first()
            if not self.coupon:
                self.msg = _(u'优惠券不存在')
                return False

            # 优惠券金额
            if (self.coupon.is_valid == 1 and
                self.coupon.begin_time <= self.current_time and
                self.coupon.end_time >= self.current_time and
                self.coupon.limit_amount <= self.items_amount):
                self.coupon_amount   = Decimal(self.coupon.coupon_amount)
                self.discount_amount = self.coupon_amount

        # 应付金额
        self.pay_amount = self.items_amount + self.shipping_amount - self.discount_amount

        return True


class CartStaticMethodsService(object):
    """购物车静态方法Service"""

    @staticmethod
    def pay_page(order_id, uid):
        """订单支付页面"""

        is_weixin = toint(request.args.get('is_weixin', '0'))

        # 检查
        order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
        if not order:
            return (False, u'', {}, request.headers['Referer'])
        
        order_address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()
        coupon        = Coupon.query.filter(Coupon.order_id == order_id).first()
        funds         = Funds.query.filter(Funds.uid == uid).first()

        shipping_title = _(u'%s  ￥%s(满￥%s免运费)' %\
                            (order.shipping_name, order.shipping_amount, order.free_limit_amount))

        data = {'order':order, 'order_address':order_address, 'coupon':coupon,
                'shipping_title':shipping_title, 'funds':funds.funds, 'is_weixin':is_weixin}
        return (True, u'', data, u'')

    @staticmethod
    def checkout_page(uid, client):
        """结算页面"""

        args         = request.args
        current_time = current_timestamp()

        # 立即购买或结算
        buy_now = toint(args.get('buy_now', '0'))
        if buy_now == 1:
            goods_id = toint(args.get('goods_id', '0'))

            # 检查
            if goods_id <= 0:
                return (False, u'', {}, request.headers['Referer'])

            # 检查
            goods = Goods.query.get(goods_id)
            if not goods:
                return (False, u'', {}, request.headers['Referer'])

            # 删除
            _cart = Cart.query.\
                            filter(Cart.uid == uid).\
                            filter(Cart.goods_id == goods_id).\
                            filter(Cart.checkout_type == 2).first()
            if _cart:
                model_delete(_cart, commit=True)

            data = {'uid':uid, 'goods_id':goods_id, 'quantity':1, 'is_checked':1, 'checkout_type':2,
                    'add_time':current_time, 'update_time':current_time}
            cart = model_create(Cart, data, commit=True)

            carts_id = [cart.cart_id]
        else:
            carts_id = args.get('carts_id', '[]').strip()
            try:
                carts_id = json.loads(carts_id)
                carts_id = [toint(cart_id) for cart_id in carts_id]
            except Exception as e:
                return (False, u'', {}, url_for('%s.cart.root' % client, msg=_(u'系统错误:参数错误')))

        # 钱包
        funds = Funds.query.filter(Funds.uid == uid).first()

        # 快递列表
        _shipping_list = Shipping.query.\
                            filter(Shipping.is_enable == 1).\
                            order_by(Shipping.sorting.desc(), Shipping.shipping_amount.asc()).all()
        if len(_shipping_list) <= 0:
            return (False, u'', {}, url_for('%s.cart.root' % client, msg=_(u'系统末配置快递')))

        # 默认快递
        default_shipping = Shipping.query.\
                                filter(Shipping.is_enable == 1).\
                                filter(Shipping.is_default == 1).first()
        default_shipping = default_shipping if default_shipping else _shipping_list[0]

        cs = CheckoutService(uid, carts_id, default_shipping.shipping_id)
        if not cs.check():
            return (False, u'', {}, url_for('%s.cart.root' % client, msg=cs.msg))

        # 收货地址
        addresses       = UserAddress.query.\
                            filter(UserAddress.uid == uid).\
                            order_by(UserAddress.is_default.desc()).\
                            order_by(UserAddress.ua_id.desc()).all()
        default_address = UserAddress.query.\
                            filter(UserAddress.uid == uid).\
                            filter(UserAddress.is_default == 1).first()
        if not default_address:
            default_address = UserAddress.query.\
                                filter(UserAddress.uid == uid).\
                                order_by(UserAddress.ua_id.desc()).first()

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
            titel    = _(u'%s  ￥%s(满￥%s免运费)' %\
                        (_s.shipping_name, _s.shipping_amount, _s.free_limit_amount))
            shipping = u'{"title":"%s", "value":%s}' % (titel, _s.shipping_id)
            shipping_list.append(shipping)
        shipping_list  = ','.join(shipping_list)
        shipping_list  = '[%s]' % shipping_list
        shipping_title = _(u'%s  ￥%s(满￥%s免运费)' %\
                            (default_shipping.shipping_name, default_shipping.shipping_amount,
                            default_shipping.free_limit_amount))

        carts_id = [cart_id.__str__() for cart_id in carts_id]
        carts_id = ','.join(carts_id)

        data = {'carts':cs.carts, 'carts_id':carts_id, 'items_amount':cs.items_amount,
                'shipping_amount':cs.shipping_amount.quantize(Decimal('0.00')),
                'discount_amount':cs.discount_amount, 'pay_amount':cs.pay_amount,
                'addresses':addresses, 'default_address':default_address,
                'shipping_list':shipping_list, 'default_shipping':default_shipping,
                'shipping_title':shipping_title, 'coupons':coupons, 'funds':funds.funds}
        return (True, u'', data, u'')
