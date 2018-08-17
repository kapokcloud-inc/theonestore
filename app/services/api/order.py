# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import requests
import json
import random
from decimal import Decimal

from flask import (
    abort,
    session
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination
from sqlalchemy import or_

from app.database import db

from app.helpers import (
    model_create,
    model_update,
    model_delete,
    log_info,
    log_error,
    toint,
    get_count
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str,
    before_after_timestamp
)

from app.services.message import MessageCreateService
from app.services.api.cart import (
    CheckoutService,
    CartService
)
from app.services.api.funds import FundsService

from app.models.aftersales import Aftersales
from app.models.coupon import Coupon
from app.models.shipping import Shipping
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


class OrderException(Exception):
    pass


class OrderCreateService(object):
    """创建订单Service"""

    def __init__(self, uid, carts_id, ua_id, shipping_id=0, coupon_id=0, user_remark=''):
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
        """检查 - 购物车商品项"""

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
        """检查"""

        if not self._check_shipping_address():
            return False

        if not self._check_shopping_cart():
            return False

        return True

    def create(self):
        """创建订单"""

        # 订单冗余商品数据
        order_items = []

        # 创建订单索引
        order_index = model_create(OrderIndex, {}, commit=True)
        order_id    = order_index.order_id

        # 创建订单编号
        order_sn = OrderStaticMethodsService.create_order_sn(self.current_time)

        # 创建订单地址
        data = {'order_id':order_id, 'name':self.shipping_address.name, 'mobile':self.shipping_address.mobile,
                'province':self.shipping_address.province, 'city':self.shipping_address.city,
                'district':self.shipping_address.district, 'address':self.shipping_address.address,
                'zip':self.shipping_address.zip, 'add_time':self.current_time, 'update_time':self.current_time}
        model_create(OrderAddress, data)

        # 使用优惠券
        if self.coupon:
            data = {'is_valid':0 , 'order_id':order_id, 'use_time':self.current_time}
            model_update(self.coupon, data)

            self.discount_desc = _(u'使用优惠券%s: %s' % (self.coupon.coupon_id, self.coupon.coupon_name))

        # 更新订单金额
        self.order_amount = self.items_amount + self.shipping_amount

        # 创建订单商品等
        for _cart in self.carts:
            cart = _cart['cart']
            item = _cart['item']

            # 创建订单商品
            data = {'order_id':order_id, 'goods_id':item.goods_id, 'goods_name':item.goods_name, 'goods_img':item.goods_img,
                    'goods_desc':item.goods_desc, 'goods_quantity':cart.quantity, 'goods_price':item.goods_price,
                    'add_time':self.current_time}
            model_create(OrderGoods, data)

            # 订单冗余商品数据
            order_items.append({'goods_id':item.goods_id, 'goods_name':item.goods_name, 'goods_img':item.goods_img,
                                'goods_desc':item.goods_desc, 'goods_price':item.goods_price.__str__(),
                                'quantity':cart.quantity})

        # 订单冗余商品数据
        goods_data = json.dumps(order_items)

        # 创建订单
        data = {'order_id':order_id, 'order_sn':order_sn, 'uid':self.uid, 'order_type':1, 'order_status':1,
                'goods_amount':self.items_amount, 'order_amount':self.order_amount,
                'discount_amount':self.discount_amount, 'discount_desc':self.discount_desc,
                'pay_amount':self.pay_amount, 'pay_type':1, 'pay_status':1, 'shipping_id':self.shipping_id,
                'shipping_name':self.shipping.shipping_name, 'shipping_code':self.shipping.shipping_code,
                'shipping_amount':self.shipping_amount, 'free_limit_amount':self.shipping.free_limit_amount,
                'shipping_status':1, 'deliver_status':0, 'user_remark':self.user_remark, 'goods_quantity':self.items_quantity,
                'goods_data':goods_data, 'add_time':self.current_time, 'update_time':self.current_time}
        self.order = model_create(Order, data)

        # 删除购物车商品项
        for cart_id in self.carts_id:
            cart = Cart.query.get(cart_id)
            model_delete(cart)

        # 站内消息
        content = _(u'您的订单%s已创建，请尽快完成支付。' % order_sn)
        mcs = MessageCreateService(1, self.order.uid, -1, content, ttype=1, tid=order_id, current_time=self.current_time)
        if not mcs.check():
            log_error('[ErrorServiceApiOrderOrderCreateServiceCreate][MessageCreateError]  order_id:%s msg:%s' %\
                (order_id, mcs.msg))
        else:
            mcs.do()

        db.session.commit()

        cs = CartService(self.uid, 0)
        cs.check()
        session['cart_total'] = cs.cart_total

        return True


class OrderUpdateService(object):
    """更新订单Service"""

    def __init__(self, uid, order_id, ua_id, shipping_id=0, coupon_id=0):
        self.msg              = ''
        self.uid              = uid                    # 购买人
        self.order_id         = order_id               # 订单ID
        self.ua_id            = ua_id                  # 收货地址ID
        self.shipping_id      = shipping_id            # 配送方式ID
        self.coupon_id        = coupon_id              # 优惠券ID
        self.current_time     = current_timestamp()    # 当前时间

        self.order            = None                   # 订单实例
        self.shipping_address = None                   # 收货地址实例
        self.order_address    = None                   # 已用订单地址实例
        self.shipping         = None                   # 配送方式实例
        self.coupon           = None                   # 优惠券实例
        self._coupon          = None                   # 已用优惠券实例
        self.items_amount     = Decimal('0.00')        # 订单商品总金额
        self.shipping_amount  = Decimal('0.00')        # 快递费用
        self.order_amount     = Decimal('0.00')        # 订单金额: items_amount + shipping_amount
        self.discount_amount  = Decimal('0.00')        # 订单优惠金额: 使用优惠券等优惠金额
        self.pay_amount       = Decimal('0.00')        # 订单应付金额: order_amount - discount_amount

    def _check_order(self):
        """检查 - 订单"""

        self.order = Order.query.filter(Order.order_id == self.order_id).filter(Order.uid == self.uid).first()
        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        if self.order.pay_status != 1:
            self.msg = _(u'不能修改已支付的订单')
            return False

        self.items_amount = Decimal(self.order.goods_amount)

        return True

    def _check_shipping_address(self):
        """检查 - 收货地址"""

        self.order_address = OrderAddress.query.filter(OrderAddress.order_id == self.order_id).first()

        self.shipping_address = UserAddress.query.filter(UserAddress.ua_id == self.ua_id).\
                                    filter(UserAddress.uid == self.uid).first()
        if not self.shipping_address:
            self.msg = _(u'收货地址不存在')
            return False

        return True

    def _check_shipping(self):
        """检查 - 快递"""

        self.shipping = Shipping.query.get(self.shipping_id)
        if not self.shipping:
            self.msg = _(u'快递不存在')
            return False

        self.shipping_amount = Decimal(self.shipping.shipping_amount)

        return True

    def _check_coupon(self):
        """检查 - 优惠券"""

        self._coupon = Coupon.query.filter(Coupon.order_id == self.order_id).first()
        _coupon_id   = self._coupon.coupon_id if self._coupon else None

        if self.coupon_id > 0 and self.coupon_id != _coupon_id:
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

        return True

    def check(self):
        """检查"""

        if not self._check_order():
            return False

        if not self._check_shipping_address():
            return False

        if not self._check_shipping():
            return False

        if not self._check_coupon():
            return False

        return True

    def update(self):
        """更新订单"""

        discount_desc = None

        # 删除已用订单地址
        model_delete(self.order_address)

        # 创建订单地址
        data = {'order_id':self.order_id, 'name':self.shipping_address.name, 'mobile':self.shipping_address.mobile,
                'province':self.shipping_address.province, 'city':self.shipping_address.city,
                'district':self.shipping_address.district, 'address':self.shipping_address.address,
                'zip':self.shipping_address.zip, 'add_time':self.current_time, 'update_time':self.current_time}
        model_create(OrderAddress, data)

        # 还原已用优惠券
        if self._coupon and self._coupon != self.coupon:
            data = {'is_valid':1 , 'order_id':0, 'use_time':0}
            model_update(self._coupon, data)

            discount_desc = ''

        # 使用优惠券
        if self.coupon:
            data = {'is_valid':0 , 'order_id':self.order_id, 'use_time':self.current_time}
            model_update(self.coupon, data)

            discount_desc = _(u'使用优惠券%s: %s' % (self.coupon.coupon_id, self.coupon.coupon_name))

        # 更新订单金额
        self.order_amount = self.items_amount + self.shipping_amount

        # 更新应付金额
        self.pay_amount = self.order_amount - self.discount_amount

        # 更新订单
        data = {'goods_amount':self.items_amount, 'order_amount':self.order_amount,
                'discount_amount':self.discount_amount, 'pay_amount':self.pay_amount,
                'shipping_id':self.shipping_id, 'shipping_name':self.shipping.shipping_name,
                'shipping_code':self.shipping.shipping_code, 'shipping_amount':self.shipping_amount,
                'update_time':self.current_time}

        if discount_desc is not None:
            data['discount_desc'] = discount_desc

        model_update(self.order, data)

        db.session.commit()

        return True


class RechargeOrderCreateService(object):
    """创建充值订单Service"""

    def __init__(self, uid, recharge_amount):
        self.msg             = ''
        self.uid             = uid                    # 购买人
        self.recharge_amount = recharge_amount        # 充值金额
        self.current_time    = current_timestamp()    # 当前时间
        self.order           = None                   # 订单实例

    def check(self):
        """检查"""

        try:
            self.recharge_amount = Decimal(self.recharge_amount)
        except Exception as e:
            self.msg = _(u'充值金额无效')
            return False

        if self.recharge_amount <= 0:
            self.msg = _(u'充值金额不能小于或等于0')
            return False

        return True

    def create(self):
        """创建订单"""

        # 创建订单索引
        order_index = model_create(OrderIndex, {}, commit=True)
        order_id    = order_index.order_id

        # 创建订单编号
        order_sn = OrderStaticMethodsService.create_order_sn(self.current_time)

        # 订单商品总金额
        goods_amount = self.recharge_amount

        # 更新订单金额
        order_amount = goods_amount

        # 更新订单应付金额
        pay_amount = order_amount

        # 创建订单
        data = {'order_id':order_id, 'order_sn':order_sn, 'uid':self.uid, 'order_type':2, 'order_status':1,
                'goods_amount':goods_amount, 'order_amount':order_amount,
                'pay_amount':pay_amount, 'pay_type':1, 'pay_status':1,
                'add_time':self.current_time, 'update_time':self.current_time}
        self.order = model_create(Order, data)

        db.session.commit()

        return True


class PayService(object):
    """订单支付Service"""

    def __init__(self, uid, order_id_list):
        self.msg            = ''
        self.uid            = uid
        self.order_id_list  = order_id_list
        self.order_id_json  = '[]'
        self.order_sn_list  = []
        self.pay_order_list = []
        self.tran           = None
        self.current_time   = current_timestamp()

    def check_order_list(self):
        """检查支付订单列表"""

        for order in self.pay_order_list:
            self.order_sn_list.append(order.order_sn)

        return True

    def check(self):
        """检查"""

        # 检查 - 支付订单ID列表数据
        self.order_id_list = [toint(order_id) for order_id in self.order_id_list]
        if len(self.order_id_list) <= 0:
            self.msg = _(u'支付订单ID列表不能为空')
            return False

        # 格式化支付订单ID列表数据
        self.order_id_list.sort()
        self.order_id_json = json.dumps(self.order_id_list)

        # 支付订单列表
        q = db.session.query(Order.order_id, Order.order_sn, Order.pay_amount, Order.order_type, Order.uid).\
                    filter(Order.uid == self.uid).\
                    filter(Order.pay_status == 1).\
                    filter(Order.order_id.in_(self.order_id_list))

        # 检查 - 支付订单列表是否有非法的订单
        if len(self.order_id_list) != get_count(q):
            self.msg = _(u'创建支付失败')
            return False

        # 支付订单列表
        self.pay_order_list = q.all()

        # 支付订单列表对应的交易
        self.tran = OrderTran.query.filter(OrderTran.uid == self.uid).\
                    filter(OrderTran.order_id_list == self.order_id_json).first()
        if self.tran:
            # 检查交易是否已经支付
            if self.tran.pay_status == 2:
                self.msg = _(u'该订单已经支付过了')
                return False

            # 检查 - 支付订单列表
            if not self.check_order_list():
                return False

            return True

        # 检查 - 支付订单列表
        if not self.check_order_list():
            return False

        return True


    def create_tran(self):
        """创建交易"""

        pay_amount = Decimal('0.00')
        for pay_order in self.pay_order_list:
            pay_amount += Decimal(pay_order.pay_amount)

        tran_index = model_create(OrderTranIndex, {}, commit=True)

        data = {'tran_id':tran_index.tran_id, 'uid':self.uid, 'pay_amount':pay_amount,
                'pay_status':1, 'order_id_list':self.order_id_json,
                'add_time':self.current_time, 'update_time':self.current_time}
        self.tran = model_create(OrderTran, data, commit=True)

        return True


class PaidService(object):
    """订单已经支付Service"""

    def __init__(self, tran_id, **kwargs):
        self.tran_id      = tran_id
        self.kwargs       = kwargs
        self.current_time = current_timestamp()

    def paid(self):
        """已付款业务处理"""

        pay_tran_id = self.kwargs.get('pay_tran_id', '')
        pay_method  = self.kwargs.get('pay_method', '')
        paid_time   = self.kwargs.get('paid_time', self.current_time)
        paid_amount = Decimal(self.kwargs.get('paid_amount', '0.00'))

        log_info('[InfoServiceApiOrderPaidServicePaid] tran_id:%s paid_amount:%.2f' % (self.tran_id, paid_amount))

        # 检查 - 交易
        tran = OrderTran.query.get(self.tran_id)
        if not tran:
            log_info('[InfoServiceApiOrderPaidServicePaid] not found tran: tran_id:%s' % self.tran_id)
            raise OrderException(_(u'找不到订单'))

        # 检查 - 订单
        order_id_list = json.loads(tran.order_id_list)
        order_list = Order.query.filter(Order.order_id.in_(order_id_list)).all()
        if not order_list:
            log_info('[InfoServiceApiOrderPaidServicePaid] not found order list: tran_id:%s' % self.tran_id)
            raise OrderException(_(u'找不到订单'))

        # 检查 - 是否已经处理过
        if tran.pay_status == 2:
            log_info('[InfoServiceApiOrderPaidServicePaid] do already: tran_id:%s' % self.tran_id)
            return tran

        # 更新交易
        model_update(tran, {'pay_status':2, 'pay_method':pay_method, 'paid_time':paid_time})

        # 更新交易 - 支付流水号
        if pay_tran_id:
            model_update(tran, {'pay_tran_id':pay_tran_id})

        # 提交交易事务
        db.session.commit()

        # 遍历更新订单及订单商品等
        for order in order_list:
            order_id = order.order_id

            # 更新订单
            data = {'tran_id':self.tran_id, 'pay_method':tran.pay_method, 'pay_status':2, 'pay_tran_id':tran.pay_tran_id,
                    'paid_time':paid_time, 'paid_amount':order.pay_amount, 'update_time':paid_time}

            # 普通订单
            if order.order_type == 1:
                # 订单商品列表
                og_list = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
                for og in og_list:
                    goods = Goods.query.get(og.goods_id)
                    if goods:
                        # 销量
                        sale_count = goods.sale_count + og.goods_quantity

                        # 库存
                        stock_quantity = goods.stock_quantity - og.goods_quantity

                        # 更新商品
                        model_update(goods, {'sale_count':sale_count, 'stock_quantity':stock_quantity})

                # 更新订单
                data['shipping_status'] = 1

            # 充值订单
            if order.order_type == 2:
                # 更新余额 - 充值 - 检查
                remark_user = u'充值'
                remark_sys  = u'充值: 订单ID:%s 支付方式:%s 第三方支付流水号:%s' % (order_id, tran.pay_method, tran.pay_tran_id)
                fs = FundsService(order.uid, order.goods_amount, 1, 1, self.tran_id, remark_user, remark_sys, paid_time)
                if not fs.check():
                    log_error('[ErrorServiceApiOrderPaidServicePaid][FundsServiceError01]  remark_sys:%s' % remark_sys)
                    continue

                # 更新余额 - 充值
                fs.update()

            model_update(order, data)

            # 站内消息
            if order.order_type == 1:
                content = _(u'您的订单%s已支付，我们会尽快发货。' % order.order_sn)
                mcs = MessageCreateService(1, order.uid, -1, content, ttype=1, tid=order_id, current_time=self.current_time)
                if not mcs.check():
                    log_error('[ErrorServiceApiOrderPaidServicePaid][MessageCreateError]  order_id:%s msg:%s' %\
                                (order_id, mcs.msg))
                else:
                    mcs.do()

            # 提交订单事务
            db.session.commit()

        return True


class OrderCancelService(object):
    """取消订单Service"""

    def __init__(self, order_id, uid, cancel_desc=u''):
        self.msg           = ''
        self.order_id      = order_id               # 订单ID
        self.uid           = uid                    # 订单用户ID
        self.cancel_desc   = cancel_desc            # 取消原因
        self.order         = None                   # 订单
        self.current_time  = current_timestamp()
        self.cancel_status = 0

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def check(self):
        """检查"""

        self.order = Order.query.filter(Order.order_id == self.order_id).filter(Order.uid == self.uid).first()

        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        if self.order.pay_status == 2:
            self.msg = _(u'订单已支付，不能取消， 请联系客服。')
            return False

        if self.order.order_status == 2:
            self.msg = _(u'订单已经完成，不能取消。')
            return False

        if self.order.order_status == 3:
            self.msg = _(u'订单已经取消过了')
            return False

        self.cancel_status = 3

        return True

    def cancel(self):
        """取消"""

        data = {'order_status':3, 'cancel_status':self.cancel_status, 'cancel_desc':self.cancel_desc,
                'cancel_time':self.current_time, 'update_time':self.current_time}
        model_update(self.order, data)

        # 站内消息
        content = _(u'您的订单%s已取消。' % self.order.order_sn)
        mcs = MessageCreateService(1, self.order.uid, -1, content, ttype=1, tid=self.order.order_id,
                                    current_time=self.current_time)
        if not mcs.check():
            log_error('[ErrorServiceApiOrderOrderCancelServiceCancel][MessageCreateError]  order_id:%s msg:%s' %\
                (self.order.order_id, mcs.msg))
        else:
            mcs.do()

        return True


class OrderDeliverService(object):
    """确认收货Service"""

    def __init__(self, order_id, uid):
        self.msg              = ''
        self.order_id         = order_id            # 订单ID
        self.uid              = uid                 # 用户ID
        self.current_time     = current_timestamp() # 当前时间
        self.order            = None                # 订单实例

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def check(self):
        """检查"""

        self.order = Order.query.filter(Order.order_id == self.order_id).\
                            filter(Order.uid == self.uid).first()
        if self.order is None:
            self.msg = _(u'找不到订单')
            return False

        if self.order.shipping_status != 2:
            self.msg = _(u'商品还没有发货，不能确认收货')
            return False

        if self.order.deliver_status == 2:
            self.msg = _(u'已经确认过发货，请勿重复确认')
            return True

        return True

    def deliver(self):
        """确认收货"""

        data = {'order_status':2, 'deliver_status':2, 'deliver_time':self.current_time}
        model_update(self.order, data)

        # 站内消息
        content = _(u'您的订单%s已确认签收，请前往评价。' % self.order.order_sn)
        mcs = MessageCreateService(1, self.order.uid, -1, content, ttype=1, tid=self.order.order_id,
                                    current_time=self.current_time)
        if not mcs.check():
            log_error('[ErrorServiceApiOrderOrderDeliverServiceDeliver][MessageCreateError]  order_id:%s msg:%s' %\
                (self.order.order_id, mcs.msg))
        else:
            mcs.do()


class OrderStaticMethodsService(object):
    """订单静态方法Service"""

    @staticmethod
    def create_order_sn(current_time):
        """创建订单编号"""

        current_time = timestamp2str(current_time, 'YYYYMMDDHHmmss')
        randint      = random.randint(1000, 9999)
        order_sn     = '%s%s' % (current_time, randint)

        order = Order.query.filter(Order.order_sn == order_sn).first()
        if order:
            order_sn = OrderStaticMethodsService.create_order_sn(current_time)

        return order_sn

    @staticmethod
    def orders(uid, params, is_pagination=False):
        """获取订单列表"""

        p            = toint(params.get('p', '1'))
        ps           = toint(params.get('ps', '10'))
        tab_status   = toint(params.get('tab_status', '0'))     # 标签状态: 0.全部; 1.待付款; 2.待收货; 3.已完成; 4.已取消;

        q = db.session.query(Order.order_id, Order.order_sn, Order.order_status, Order.order_amount, Order.pay_status,
                            Order.shipping_amount, Order.shipping_status, Order.deliver_status,
                            Order.goods_quantity, Order.goods_data, Order.add_time,Order.shipping_time).\
                filter(Order.uid == uid).\
                filter(Order.order_type == 1).\
                filter(Order.is_remove == 0)

        if tab_status == 1:
            q = q.filter(Order.order_status == 1).filter(Order.pay_status == 1)

        if tab_status == 2:
            q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).filter(Order.deliver_status.in_([0,1]))

        if tab_status == 3:
            q = q.filter(Order.order_status == 2).filter(Order.pay_status == 2).filter(Order.deliver_status == 2)

        if tab_status == 4:
            current_time = current_timestamp()
            min_pay_time = before_after_timestamp(current_time, {'days':1})

            q = q.filter(or_((Order.add_time >= min_pay_time), (Order.order_status == 3)))

        orders = q.order_by(Order.order_id.desc()).offset((p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        texts = {}
        codes = {}
        aftersales = {}
        for order in orders:
            text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)
            texts[order.order_id] = text
            codes[order.order_id] = code
            aftersale = Aftersales.query.filter(Aftersales.order_id == order.order_id).filter(Aftersales.status.in_([1,2,3])).first()
            if aftersale:
                aftersales[order.order_id] = aftersale
            
        return {'orders':orders, 'pagination':pagination, 'texts':texts, 'codes':codes,'aftersales':aftersales,'current_time':current_timestamp()}

    @staticmethod
    def order_status_text_and_action_code(order, min_pay_time=0):
        """获取订单状态和订单指令"""

        status_text = u''   # 订单状态: 已取消; 待付款; 待收货; 待评价; 已完成;
        action_code = []    # 订单指令: 0.无指令; 1.付款; 2.取消订单; 3.查看物流; 4.确认收货; 5.再次购买; 6.删除订单; 7.申请售后;

        current_time = current_timestamp()
        min_pay_time = min_pay_time if min_pay_time else before_after_timestamp(current_time, {'days':1})

        if order.order_status == 1:
            if order.pay_status == 1:
                if order.add_time < min_pay_time:
                    status_text = _(u'待付款')
                    action_code = [1,2,5]

                    return (status_text, action_code)

                if order.add_time >= min_pay_time:
                    status_text = _(u'已取消')
                    action_code = [5,6]

                    return (status_text, action_code)

            if order.pay_status == 2:
                if order.shipping_status == 1:
                    status_text = _(u'待收货')
                    action_code = [5,7]

                    return (status_text, action_code)

                if order.shipping_status == 2 and order.deliver_status == 1:
                    status_text = _(u'待收货')
                    action_code = [3,4,5,7]

                    return (status_text, action_code)

        if order.order_status == 2:
            status_text = _(u'已完成')
            action_code = [3,5,6,7]

            return (status_text, action_code)

        if order.order_status == 3:
            status_text = _(u'已取消')
            action_code = [5,6]

            return (status_text, action_code)

        return (status_text, action_code)

    @staticmethod
    def track(com, code):
        """查询物流"""

        # 查询
        data = {'type':com, 'postid':code, 'id':1, 'valicode':'', 'temp':'0.49738534969422676'}
        url  = 'https://m.kuaidi100.com/query'
        res  = requests.post(url, data=data)
        res.encoding = 'utf8'

        # 检查 - 获取验证信息
        if res.status_code != 200:
            return (_(u'查询失败'), [])

        data = res.json()
        if data['message'] != 'ok':
            return (_(u'查询失败'), [])

        return ('ok', data['data'])

    @staticmethod
    def detail_page(order_id, uid):
        """详情页面"""

        order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
        if not order:
            return abort(404)

        items         = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
        order_address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()
        text, code    = OrderStaticMethodsService.order_status_text_and_action_code(order)

        express_data  = None
        express_datas = []
        if order.shipping_status == 2:
            _express_msg, _express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)
            if _express_msg == 'ok':
                express_data  = _express_data[0] if len(_express_data) > 0 else {}
                express_datas = _express_data

        aftersale = Aftersales.query.filter(Aftersales.order_id == order_id).filter(Aftersales.status.in_([1,2,3])).first()

        data = {'order':order, 'items':items, 'order_address':order_address,
                'text':text, 'code':code, 'express_data':express_data, 'express_datas':express_datas,
                'aftersale':aftersale, 'current_time':current_timestamp()}
        return data
