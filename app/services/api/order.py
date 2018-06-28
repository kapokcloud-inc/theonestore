# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import random
from decimal import Decimal

from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    model_create,
    model_update,
    model_delete,
    log_info,
    toint
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str
)

from app.services.api.cart import CheckoutService

from app.models.user import UserAddress
from app.models.item import Goods
from app.models.cart import Cart
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderIndex,
    OrderTran,
    OrderTranIndex
)


class OrderCreateService(object):
    """ 创建订单Service """

    def __init__(self, uid, carts_id, ua_id, shipping_id=0, coupon_id='', user_remark=''):
        self.msg               = ''
        self.uid               = uid                    # 购买人
        self.carts_id          = carts_id               # 购物车商品项ID列表
        self.ua_id             = ua_id                  # 收货地址ID
        self.shipping_id       = shipping_id            # 配送方式ID
        self.coupon_id         = coupon_id              # 优惠券ID
        self.user_remark       = user_remark            # 用户备注
        self.current_time      = current_timestamp()    # 当前时间

        self.order             = None                   # 订单实例
        self.shipping_address  = None                   # 收货地址实例
        self.shipping          = None                   # 配送方式实例
        self.coupon            = None                   # 优惠券实例
        self.cs                = None                   # 结算Service实例
        self.carts             = []                     # 购物车商品项列表
        self.items_amount      = Decimal('0.00')        # 订单商品总金额
        self.items_quantity    = 0                      # 订单商品总件数
        self.shipping_amount   = Decimal('0.00')        # 快递费用
        self.order_amount      = Decimal('0.00')        # 订单金额: items_amount + shipping_amount
        self.discount_amount   = Decimal('0.00')        # 订单优惠金额: 使用优惠券等优惠金额
        self.discount_desc     = u''                    # 订单优惠说明
        self.pay_amount        = Decimal('0.00')        # 订单应付金额: order_amount - discount_amount

    def _check_shipping_address(self):
        """检查 - 收货地址"""

        self.shipping_address = UserAddress.query.filter(UserAddress.ua_id == self.ua_id).\
                                    filter(UserAddress.uid == self.uid).first()
        if not self.shipping_address:
            self.msg = _(u'收货地址不存在')
            return False

        return True

    def _check_shopping_cart(self):
        """ 检查 - 购物车商品项 """

        if len(self.carts_id) == 0:
            self.msg = _(u'购物车为空')
            return False

        self.cs = CheckoutService(self.uid, self.carts_id, self.shipping_id, self.coupon_id)
        if not self.cs.check():
            self.msg = self.cs.msg
            return False

        self.items_amount    = self.cs.items_amount
        self.items_quantity  = self.cs.items_quantity
        self.shipping_amount = self.cs.shipping_amount
        self.discount_amount = self.cs.discount_amount
        self.pay_amount      = self.cs.pay_amount
        self.carts           = self.cs.carts
        self.coupon          = self.cs.coupon
        self.shipping        = self.cs.shipping

        return True

    def check(self):
        """ 检查 """

        if not self._check_shipping_address():
            return False

        if not self._check_shopping_cart():
            return False

        return True

    def create(self):
        """ 创建订单 """

        # 订单冗余商品数据
        order_items = []

        # 创建订单索引
        order_index = model_create(OrderIndex, {}, commit=True)
        order_id    = order_index.order_id

        # 创建订单编号
        order_sn = OrderStaticMethodsService.create_order_sn(self.current_time)

        # 使用优惠券
        if self.coupon:
            data = {'is_valid':0 , 'order_id':order_id, 'use_time':self.current_time}
            model_update(self.coupon, data)

            self.discount_desc = _(u'使用优惠券%s: %s' % (self.coupon.coupon_id, self.coupon.coupon_name))

        # 更新订单金额
        self.order_amount = self.items_amount + self.shipping_amount

        # 创建收货地址
        data = {'order_id':order_id, 'name':self.shipping_address.name, 'mobile':self.shipping_address.mobile,
                'province':self.shipping_address.province, 'city':self.shipping_address.city,
                'district':self.shipping_address.district, 'address':self.shipping_address.address,
                'zip':self.shipping_address.zip, 'add_time':self.current_time, 'update_time':self.current_time}
        model_create(OrderAddress, data)

        # 创建订单商品等
        for _cart in self.carts:
            cart = _cart['cart']
            item = _cart['item']

            # 创建订单商品
            data = {'order_id':order_id, 'goods_id':item.goods_id, 'goods_name':item.goods_name,
                    'goods_img':item.goods_img, 'goods_quantity':cart.quantity, 'goods_price':item.goods_price,
                    'add_time':self.current_time}
            model_create(OrderGoods, data)

            # 订单冗余商品数据
            order_items.append({'goods_id':item.goods_id, 'goods_name':item.goods_name, 'goods_img':item.goods_img,
                                'goods_price':item.goods_price.__str__(), 'quantity':cart.quantity})

        # 订单冗余商品数据
        goods_data = json.dumps(order_items)

        # 创建订单
        data = {'order_id':order_id, 'order_sn':order_sn, 'uid':self.uid, 'order_type':1, 'order_status':1,
                'goods_amount':self.items_amount, 'order_amount':self.order_amount,
                'discount_amount':self.discount_amount, 'discount_desc':self.discount_desc,
                'pay_amount':self.pay_amount, 'pay_type':1, 'pay_status':1, 'shipping_id':self.shipping_id,
                'shipping_name':self.shipping.shipping_name, 'shipping_code':self.shipping.shipping_code,
                'shipping_amount':self.shipping_amount, 'shipping_status':1, 'deliver_status':0,
                'user_remark':self.user_remark, 'goods_quantity':self.items_quantity, 'goods_data':goods_data,
                'add_time':self.current_time, 'update_time':self.current_time}
        self.order = model_create(Order, data)

        # 删除购物车商品项 ??
        #for cart_id in self.carts_id:
        #    cart = Cart.query.get(cart_id)
        #    model_delete(cart)

        db.session.commit()

        return True


class OrderStaticMethodsService(object):
    """订单静态方法Service"""

    @staticmethod
    def create_order_sn(current_time):
        """创建订单编号"""

        current_time = timestamp2str(current_time, 'YYYYMMDDHH:mm:ss')
        randint      = random.randint(1000, 9999)
        order_sn     = '%s%s' % (current_time, randint)

        order = Order.query.filter(Order.order_sn == order_sn).first()
        if order:
            order_sn = OrderStaticMethodsService.create_order_sn(current_time)

        return order_sn
