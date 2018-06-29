# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal

from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp

from app.models.shipping import Shipping
from app.models.coupon import Coupon
from app.models.item import Goods
from app.models.cart import Cart


class CartService(object):
    """购物车Service"""

    def __init__(self, uid, session_id):
        self.uid            = uid                   # 用户ID
        self.session_id     = session_id            # 用户session_id
        self.current_time   = current_timestamp()   # 当前时间
        self.carts          = []                    # 购物车商品项
        self.items_amount   = Decimal('0.00')       # 选中商品项商品总价
        self.items_quantity = 0                     # 选中商品项总件数
        self.total_quantity = 0                     # 商品项总件数

    def check(self):
        """检查"""

        # 购物车商品项
        q = Cart.query
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

                self.total_quantity += cart.quantity

            self.carts.append({'cart':cart, 'item':item, 'is_valid':is_valid, 'valid_status':valid_status})

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

        # 快递金额
        if self.shipping.free_limit_amount > self.items_amount:
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
