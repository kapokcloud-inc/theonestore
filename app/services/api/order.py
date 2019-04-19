# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import time
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
from sqlalchemy import (
    or_,
    func
)

from app.database import db
from app.exception import (
    TheonestoreException,
    UserException,
    AddressException,
    OrderException,
    CouponException,
    ShippingException,
    GoodsException
)

from app.helpers import (
    model_create,
    model_update,
    model_delete,
    log_info,
    log_error,
    toint,
    get_count,
    randomstr,
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str,
    before_after_timestamp
)
from app.exception import ShippingException

from app.services.weixin import WeixinMessageStaticMethodsService
from app.services.track import TrackServiceFactory
from app.services.message import MessageCreateService
from app.services.api.cart import (
    CheckoutService,
    CartService
)
from app.services.api.funds import FundsService
from app.services.response import json_encode

from app.models.coupon import Coupon
from app.models.shipping import Shipping
from app.models.user import User, UserAddress
from app.models.item import Goods
from app.models.cart import Cart
from app.models.aftersales import (
    Aftersales,
    AftersalesGoods
)
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderIndex,
    OrderTran,
    OrderTranIndex
)


class OrderService(object):
    """订单service"""

    def __init__(
            self,
            uid,
            checkout_type,
            user_address_id=0,
            cart_id_list=[],
            coupon_id=0,
            shipping_id=0,
            user_remark=''):
        """
        初始化函数
        :param int uid 用户uid
        :param int checkout_type 结算类型 1购物车 2立即购买
        :param int user_address_id 用户地址id，为0时则表示无需填写地址
        :param list cart_id_list 购物车id列表
        :param int coupon_id 优惠券id
        :param int shipping_id 快递物流id
        :param string user_remark 用户备注
        """
        self.uid = uid
        self.checkout_type = checkout_type
        self.user_address_id = user_address_id
        self.cart_id_list = cart_id_list
        self.coupon_id = coupon_id
        self.shipping_id = shipping_id
        self.user_remark = user_remark

        # 订单id
        self.order_id = 0

        # 当前时间
        self.current_time = int(time.time())

        # 用户
        self.user = User.query.get(self.uid)
        if self.user is None:
            raise UserException(_(u'用户不存在'))

        # 用户地址, 订单地址
        self.user_address = None
        self.order_address = None
        if (user_address_id > 0):
            self.user_address = UserAddress.query.\
                filter(UserAddress.uid == self.uid).\
                filter(UserAddress.ua_id == user_address_id).first()
        if self.user_address is None:
            raise AddressException(_(u'用户地址不存在'))

        # 购物车商品列表
        self.cart_goods_list = None
        self.cart_goods_list = self.get_cart_goods_list()

        # 优惠券
        self.coupon = None
        if (coupon_id > 0):
            self.coupon = Coupon.query.filter(Coupon.uid == self.uid).\
                filter(Coupon.coupon_id == self.coupon_id).\
                filter(Coupon.is_valid == 1).\
                filter(Coupon.begin_time <= self.current_time).first()
            if self.coupon is None:
                raise CouponException(_(u'优惠券不存在'))
            end_time = self.coupon.end_time
            if end_time != 0 and end_time < self.current_time:
                raise CouponException(_(u'优惠券已过期'))

        # 快递物流
        self.shipping = None
        if (shipping_id > 0):
            self.shipping = Shipping.query.get(shipping_id)
            if self.shipping is None:
                raise ShippingException(_(u'快递配置不存在'))

        # 订单信息
        self.order = Order()
        self.order.goods_amount = Decimal('0.00')
        self.order.order_amount = Decimal('0.00')
        self.order.discount_amount = Decimal('0.00')
        self.order.pay_amount = Decimal('0.00')
        self.order.paid_amount = Decimal('0.00')
        self.order.shipping_amount = Decimal('0.00')
        self.order.free_limit_amount = Decimal('0.00')
        self.order.goods_quantity = 0

        # 订单商品列表
        self.order_goods_list = None

    def get_cart_goods_list(self):
        """获取商品列表"""
        if self.cart_goods_list is not None:
            return self.cart_goods_list

        cart_goods_list = []
        if self.cart_id_list:
            cart_goods_list = db.session.query(Cart, Goods).\
                filter(Goods.goods_id == Cart.goods_id).\
                filter(Cart.cart_id.in_(self.cart_id_list)).\
                filter(Goods.is_delete == 0).\
                order_by(Cart.update_time.desc()).all()
        return cart_goods_list

    def get_goods_price(self, goods):
        """获取商品价格"""
        return Decimal(goods.goods_price)

    def create(self):
        """创建订单"""
        try:
            self.check()
        except TheonestoreException as e:
            log_error('[OrderService] [check] %s' % e)
            raise e

        # 订单id
        oi = OrderIndex()
        db.session.add(oi)
        db.session.commit()
        self.order_id = oi.order_id

        # 赋值
        self._assign_order_goods()
        self._assign_order()
        self._assign_address()
        self._assign_shipping()
        self._assign_coupon()
        self._assign_payment()

        # 删除购物车
        self._remove_cart()

        # 站内消息
        self._message()

        # 订单之后的业务
        self._commit_order_before()

        # 全部提交
        db.session.commit()

        # 处理完订单之后的业务
        self._commit_order_after()

        return self.order

    def check(self):
        """检查选项"""
        try:
            self._check_cart_goods_list()
            self._address_check()
            self._coupon_check()
            self._shipping_check()
        except TheonestoreException as e:
            raise e
        return

    def _check_cart_goods_list(self):
        """检查商品列表"""
        for (cart, goods) in self.cart_goods_list:
            if goods.is_sale == 0:
                raise GoodsException(_(u'商品已下架'))
            elif goods.stock_quantity < cart.quantity:
                raise GoodsException(_(u'库存不足'))

    def _address_check(self):
        """收件地址检查"""
        pass

    def _coupon_check(self):
        """优惠券检查"""
        if self.coupon is not None:
            if (self.coupon.limit_amount > self.order.goods_amount and
                    self.order.goods_amount > 0):
                raise CouponException(_(u'优惠券暂不可使用'))

    def _shipping_check(self):
        """快递检查"""
        pass

    def _assign_order_goods(self):
        """初始化订单商品"""
        if self.order_goods_list is not None:
            return

        goods_data_list = []
        self.order_goods_list = []
        for (cart, goods) in self.cart_goods_list:
            # 商品总价、商品数量、商品冗余json数据
            self.order.goods_amount += (
                self.get_goods_price(goods) * Decimal(cart.quantity))
            self.order.goods_quantity += cart.quantity
            goods_data = {
                'goods_id': goods.goods_id,
                'goods_name': goods.goods_name,
                'goods_img': goods.goods_img,
                'goods_desc': goods.goods_desc,
                'goods_price': self.get_goods_price(goods),
                'quantity': cart.quantity
            }
            goods_data_list.append(goods_data)

            # OrderGoods
            og = OrderGoods()
            og.order_id = self.order_id
            og.goods_id = goods.goods_id
            og.goods_name = goods.goods_name
            og.goods_img = goods.goods_img
            og.goods_desc = goods.goods_desc
            og.goods_price = self.get_goods_price(goods)
            og.goods_quantity = cart.quantity
            og.add_time = self.current_time
            db.session.add(og)
            self.order_goods_list.append(og)
        self.order.goods_data = json_encode(goods_data_list)

    def _assign_address(self):
        """赋值地址"""
        if self.user_address and not self.order_address:
            ua = self.user_address
            oa = OrderAddress()
            oa.order_id = self.order_id
            oa.name = ua.name
            oa.mobile = ua.mobile
            oa.province = ua.province
            oa.city = ua.city
            oa.district = ua.district
            oa.address = ua.address
            oa.zip = ua.zip
            oa.add_time = self.current_time
            self.order_address = oa
            db.session.add(self.order_address)

    def _assign_shipping(self):
        """赋值快递"""
        if self.shipping:
            shipping_amount = self.shipping.shipping_amount
            if self.order.goods_amount >= self.shipping.free_limit_amount:
                shipping_amount = Decimal('0.00')
            self.order.shipping_id = self.shipping.shipping_id
            self.order.shipping_name = self.shipping.shipping_name
            self.order.shipping_code = self.shipping.shipping_code
            self.order.shipping_amount = shipping_amount
            self.order.free_limit_amount = self.shipping.free_limit_amount
            self.order.shipping_status = 1  # 发货状态: 1.未发货;
            self.order.shipping_time = 0  # 发货时间

    def _assign_coupon(self):
        """初始化优惠券"""
        if self.coupon:
            self.order.discount_amount = self.coupon.coupon_amount
            self.order.discount_desc = self.coupon.coupon_name

    def _assign_payment(self):
        """赋值支付信息"""
        self.order.pay_amount = self.order.order_amount
        self.order.pay_method = 'weixin'  # alipay|weixin
        self.order.pay_type = 2  # 支付类型: 0.默认; 1.线上支付; 2.货到付款;
        self.order.pay_status = 1  # 支付状态: 0.默认; 1.待付款; 2.已付款;

    def _assign_order(self):
        """赋值订单信息"""
        self.order.uid = self.uid
        self.order.order_id = self.order_id
        self.order.order_sn = self._generate_order_sn()
        self.order.order_type = 1  # 订单类型: 0.默认; 1.普通订单; 2.充值订单;
        self.order.order_status = 1  # 订单状态: 0.默认; 1.创建订单; 2.已完成; 3.已取消; 4.已售后;
        self.order.order_amount = (
            self.order.goods_amount + self.order.shipping_amount -
            self.order.discount_amount)
        self.order.user_remark = self.user_remark
        self.order.add_time = self.current_time
        db.session.add(self.order)

    def _generate_order_sn(self):
        """生成订单编号
        规则：YYYYMMDDhhmmss + 4位随机数
        """
        sn = timestamp2str(self.current_time,
                           'YYYYMMDDHHmmss') + randomstr(4, 1)
        return sn

    def _remove_cart(self):
        """删除购物车"""
        for (cart, goods) in self.cart_goods_list:
            if cart.cart_id > 0:
                db.session.delete(cart)

    def _message(self):
        """站内消息"""
        content = _(u'您的订单%s已创建，请尽快完成支付。' % self.order.order_sn)
        mcs = MessageCreateService(
            1, self.uid, -1, content, 
            ttype=1, tid=self.order_id, current_time=self.current_time)
        if not mcs.check():
            log_error('[MessageCreateError] order_id:%s msg:%s' % (self.order_id, mcs.msg))
        else:
            mcs.do()

    def _message_push(self):
        """微信消息推送"""
        WeixinMessageStaticMethodsService.create_order(self.order)

    def _commit_order_before(self):
        """提交订单处理之前业务，子类继承实现"""
        pass

    def _commit_order_after(self):
        """提交订单处理之后，子类继承实现"""
        self._message_push()

        # 更新session中的cart_total
        if self.checkout_type == 1:
            cart_total = 0
            cart = db.session.query(func.sum(
                    Cart.quantity).label('cart_total')).\
                filter(Cart.uid == self.uid).\
                filter(Cart.checkout_type == self.checkout_type).first()
            if cart and cart.cart_total and cart.cart_total > 0:
                cart_total = cart.cart_total
            session['cart_total'] = cart_total


class OrderUpdateService(object):
    """更新订单Service"""

    def __init__(self, uid, order_id, ua_id, shipping_id=0, coupon_id=0):
        """初始化更新订单服务"""

        self.uid = uid  # 购买人
        self.order_id = order_id  # 订单ID
        self.ua_id = ua_id  # 收货地址ID
        self.shipping_id = shipping_id  # 配送方式ID
        self.coupon_id = coupon_id  # 优惠券ID
        self.current_time = current_timestamp()  # 当前时间

        self.order = None  # 订单实例
        self.shipping_address = None  # 收货地址实例
        self.order_address = None  # 已用订单地址实例
        self.shipping = None  # 配送方式实例
        self.coupon = None  # 优惠券实例
        self._coupon = None   # 已用优惠券实例
        self.items_amount = Decimal('0.00')  # 订单商品总金额
        self.shipping_amount = Decimal('0.00')   # 快递费用
        # 订单金额: items_amount + shipping_amount
        self.order_amount = Decimal('0.00')
        self.discount_amount = Decimal('0.00')  # 订单优惠金额: 使用优惠券等优惠金额
        # 订单应付金额: order_amount - discount_amount
        self.pay_amount = Decimal('0.00')

        # 是否检查
        self.__is_check_order = False
        self.__is_check_shipping_address = False
        self.__is_check_shipping = False
        self.__is_check_coupon = False
        self.__is_check = False

    def _check_order(self):
        """检查 - 订单"""
        if self.__is_check_order:
            return
        self.__is_check_order = True

        self.order = Order.query.\
            filter(Order.order_id == self.order_id).\
            filter(Order.uid == self.uid).first()

        if not self.order:
            raise OrderException(_(u'订单不存在'))

        if self.order.pay_status != 1:
            raise OrderException(_(u'不能修改已支付的订单'))

        self.items_amount = Decimal(self.order.goods_amount)

        return

    def _check_shipping_address(self):
        """检查 - 收货地址"""
        if self.__is_check_shipping_address:
            return
        self.__is_check_shipping_address = True

        self.order_address = OrderAddress.query.\
            filter(OrderAddress.order_id == self.order_id).first()

        self.shipping_address = UserAddress.query.\
            filter(UserAddress.ua_id == self.ua_id).\
            filter(UserAddress.uid == self.uid).first()

        if not self.shipping_address:
            raise OrderException(_(u'收货地址不存在'))

        return

    def _check_shipping(self):
        """检查 - 快递"""

        if self.__is_check_shipping:
            return
        self.__is_check_shipping = True

        self.shipping = Shipping.query.get(self.shipping_id)

        if not self.shipping:
            raise OrderException(_(u'快递不存在'))

        self.shipping_amount = Decimal(self.shipping.shipping_amount)

        return True

    def _check_coupon(self):
        """检查 - 优惠券"""

        if self.__is_check_coupon:
            return
        self.__is_check_coupon = True

        self._coupon = Coupon.query.\
            filter(Coupon.order_id == self.order_id).first()

        _coupon_id = self._coupon.coupon_id if self._coupon else None

        if self.coupon_id > 0 and self.coupon_id != _coupon_id:
            # 检查 - 优惠券
            self.coupon = Coupon.query.\
                filter(Coupon.coupon_id == self.coupon_id).\
                filter(Coupon.uid == self.uid).first()
            if not self.coupon:
                raise OrderException(_(u'优惠券不存在'))

            # 优惠券金额
            if (self.coupon.is_valid == 1 and
                self.coupon.begin_time <= self.current_time and
                self.coupon.end_time >= self.current_time and
                    self.coupon.limit_amount <= self.items_amount):
                self.coupon_amount = Decimal(self.coupon.coupon_amount)
                self.discount_amount = self.coupon_amount

        return

    def check(self):
        """检查"""
        if self.__is_check:
            return
        self.__is_check = True
        try:
            self._check_order()
            self._check_shipping_address()
            self._check_shipping()
            self._check_coupon()
        except OrderException as e:
            raise e

        return

    def update(self):
        """更新订单"""

        try:
            self.check()
        except OrderException as e:
            raise e

        discount_desc = None

        # 删除已用订单地址
        model_delete(self.order_address)

        # 创建订单地址
        data = {
            'order_id': self.order_id,
            'name': self.shipping_address.name,
            'mobile': self.shipping_address.mobile,
            'province': self.shipping_address.province,
            'city': self.shipping_address.city,
            'district': self.shipping_address.district,
            'address': self.shipping_address.address,
            'zip': self.shipping_address.zip,
            'add_time': self.current_time,
            'update_time': self.current_time}
        model_create(OrderAddress, data)

        # 还原已用优惠券
        if self._coupon and self._coupon != self.coupon:
            data = {
                'is_valid': 1,
                'order_id': 0,
                'use_time': 0}
            model_update(self._coupon, data)

            discount_desc = ''

        # 使用优惠券
        if self.coupon:
            data = {
                'is_valid': 0,
                'order_id': self.order_id,
                'use_time': self.current_time}
            model_update(self.coupon, data)

            discount_desc = _(u'使用优惠券%s: %s' %
                              (self.coupon.coupon_id, self.coupon.coupon_name))

        # 更新订单金额
        self.order_amount = self.items_amount + self.shipping_amount

        # 更新应付金额
        self.pay_amount = self.order_amount - self.discount_amount

        # 更新订单
        data = {
            'goods_amount': self.items_amount,
            'order_amount': self.order_amount,
            'discount_amount': self.discount_amount,
            'pay_amount': self.pay_amount,
            'shipping_id': self.shipping_id,
            'shipping_name': self.shipping.shipping_name,
            'shipping_code': self.shipping.shipping_code,
            'shipping_amount': self.shipping_amount,
            'update_time': self.current_time}

        if discount_desc is not None:
            data['discount_desc'] = discount_desc

        model_update(self.order, data)

        db.session.commit()

        return True


class RechargeOrderCreateService(object):
    """创建充值订单Service"""

    def __init__(self, uid, recharge_amount):
        self.msg = ''
        self.uid = uid                    # 购买人
        self.recharge_amount = recharge_amount        # 充值金额
        self.current_time = current_timestamp()    # 当前时间
        self.order = None                   # 订单实例

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
        order_id = order_index.order_id

        # 创建订单编号
        order_sn = OrderStaticMethodsService.create_order_sn(self.current_time)

        # 订单商品总金额
        goods_amount = self.recharge_amount

        # 更新订单金额
        order_amount = goods_amount

        # 更新订单应付金额
        pay_amount = order_amount

        # 创建订单
        data = {
            'order_id': order_id,
            'order_sn': order_sn,
            'uid': self.uid,
            'order_type': 2,
            'order_status': 1,
            'goods_amount': goods_amount,
            'order_amount': order_amount,
            'pay_amount': pay_amount,
            'pay_type': 1,
            'pay_status': 1,
            'add_time': self.current_time,
            'update_time': self.current_time}
        self.order = model_create(Order, data)
        db.session.commit()
        return True


class PayService(object):
    """订单支付Service"""

    def __init__(self, uid, order_id_list):
        self.msg = ''
        self.uid = uid
        self.order_id_list = order_id_list
        self.order_id_json = '[]'
        self.order_sn_list = []
        self.pay_order_list = []
        self.tran = None
        self.current_time = current_timestamp()

    def check_order_list(self):
        """检查支付订单列表"""

        for order in self.pay_order_list:
            self.order_sn_list.append(order.order_sn)

        return True

    def check(self):
        """检查"""

        # 检查 - 支付订单ID列表数据
        self.order_id_list = [toint(order_id)
                              for order_id in self.order_id_list]
        if len(self.order_id_list) <= 0:
            self.msg = _(u'支付订单ID列表不能为空')
            return False

        # 格式化支付订单ID列表数据
        self.order_id_list.sort()
        self.order_id_json = json.dumps(self.order_id_list)

        # 支付订单列表
        q = db.session.query(Order.order_id,
                             Order.order_sn,
                             Order.pay_amount,
                             Order.order_type,
                             Order.uid).\
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
        data = {
            'tran_id': tran_index.tran_id,
            'uid': self.uid,
            'pay_amount': pay_amount,
            'pay_status': 1,
            'order_id_list': self.order_id_json,
            'add_time': self.current_time,
            'update_time': self.current_time}
        self.tran = model_create(OrderTran, data, commit=True)
        return True

    @property
    def first_goods_name(self):
        for pay_order in self.pay_order_list:
            og = OrderGoods.query.\
                filter(OrderGoods.order_id == pay_order.order_id).\
                order_by(OrderGoods.og_id.asc()).first()
            if og is not None:
                return og.goods_name

        return u'error'


class PaidService(object):
    """订单已经支付Service"""

    def __init__(self, tran_id, **kwargs):
        self.tran_id = tran_id
        self.kwargs = kwargs
        self.current_time = current_timestamp()

    def paid(self):
        """已付款业务处理"""

        pay_tran_id = self.kwargs.get('pay_tran_id', '')
        pay_method = self.kwargs.get('pay_method', '')
        paid_time = self.kwargs.get('paid_time', self.current_time)
        paid_amount = Decimal(self.kwargs.get('paid_amount', '0.00'))

        log_info('[PaidService] tran_id:%s paid_amount:%.2f' % (
            self.tran_id, paid_amount))

        # 检查 - 交易
        tran = OrderTran.query.get(self.tran_id)
        if not tran:
            log_info(
                '[PaidService] not found tran: tran_id:%s' % self.tran_id)
            raise OrderException(_(u'找不到订单'))

        # 检查 - 订单
        order_id_list = json.loads(tran.order_id_list)
        order_list = Order.query.filter(
            Order.order_id.in_(order_id_list)).all()
        if not order_list:
            log_info(
              '[PaidService] not found order list: tran_id:%s' % self.tran_id)
            raise OrderException(_(u'找不到订单'))

        # 检查 - 是否已经处理过
        if tran.pay_status == 2:
            log_info('[PaidService] do already: tran_id:%s' % self.tran_id)
            return tran

        # 更新交易
        model_update(
            tran, {
                'pay_status': 2,
                'pay_method': pay_method,
                'paid_time': paid_time})

        # 更新交易 - 支付流水号
        if pay_tran_id:
            model_update(tran, {'pay_tran_id': pay_tran_id})

        # 提交交易事务
        db.session.commit()

        # 遍历更新订单及订单商品等
        for order in order_list:
            order_id = order.order_id

            # 更新订单
            data = {
                'tran_id': self.tran_id,
                'pay_method': tran.pay_method,
                'pay_status': 2,
                'pay_tran_id': tran.pay_tran_id,
                'paid_time': paid_time,
                'paid_amount': order.pay_amount,
                'update_time': paid_time}

            # 普通订单
            if order.order_type == 1:
                # 订单商品列表
                og_list = OrderGoods.query.filter(
                    OrderGoods.order_id == order_id).all()
                for og in og_list:
                    goods = Goods.query.get(og.goods_id)
                    if goods:
                        # 销量
                        sale_count = goods.sale_count + og.goods_quantity

                        # 库存
                        stock_quantity = goods.stock_quantity - og.goods_quantity

                        # 更新商品
                        model_update(
                            goods, {
                                'sale_count': sale_count,
                                'stock_quantity': stock_quantity})

                # 更新订单
                data['shipping_status'] = 1

            # 充值订单
            if order.order_type == 2:
                # 更新余额 - 充值 - 检查
                remark_user = _(u'充值成功')
                remark_sys = _(u'充值: 订单ID:%s 支付方式:%s 第三方支付流水号:%s' %
                               (order_id, tran.pay_method, tran.pay_tran_id))
                fs = FundsService(
                    order.uid,
                    order.goods_amount,
                    1,
                    1,
                    self.tran_id,
                    remark_user,
                    remark_sys,
                    paid_time)
                if not fs.check():
                    log_error(
                        '[FundsServiceError01]  remark_sys:%s' % remark_sys)
                    continue

                # 更新余额 - 充值
                fs.update()

            model_update(order, data)

            # 站内消息
            if order.order_type == 1:
                content = _(u'您的订单%s已支付，我们会尽快发货。' % order.order_sn)
                mcs = MessageCreateService(
                    1,
                    order.uid,
                    -1, content,
                    ttype=1,
                    tid=order_id,
                    current_time=self.current_time)
                if not mcs.check():
                    log_error('order_id:%s msg:%s' % (order_id, mcs.msg))
                else:
                    mcs.do()

            # 提交订单事务
            db.session.commit()

            # 微信消息
            if order.order_type == 2:
                WeixinMessageStaticMethodsService.recharge(order)
            else:
                WeixinMessageStaticMethodsService.paid(order)

        return True


class OrderCancelService(object):
    """取消订单Service"""

    def __init__(self, order_id, uid, cancel_desc=u''):
        """初始化服务"""

        self.order_id = order_id                  # 订单ID
        self.uid = uid                            # 订单用户ID
        self.cancel_desc = cancel_desc            # 取消原因
        self.order = None                         # 订单信息
        self.current_time = current_timestamp()   # 当前时间
        self.cancel_status = 0                    # 取消状态

        self.__is_chceck_order = False            # 是否检查订单

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def check(self):
        """检查"""

        if self.__is_chceck_order:
            return
        self.__is_chceck_order = True

        self.order = Order.query.\
            filter(Order.order_id == self.order_id).\
            filter(Order.uid == self.uid).first()

        if not self.order:
            raise OrderException(_(u'订单不存在'))

        if self.order.pay_status == 2:
            raise OrderException(_(u'订单已支付，不能取消，请联系客服'))

        if self.order.order_status == 2:
            raise OrderException(_(u'订单已经完成，不能取消'))

        if self.order.order_status == 3:
            raise OrderException(_(u'订单已经取消过了'))

        self.cancel_status = 3

        return

    def cancel(self):
        """取消"""

        try:
            self.check()
        except OrderException as e:
            raise e

        data = {
            'order_status': 3,
            'cancel_status': self.cancel_status,
            'cancel_desc': self.cancel_desc,
            'cancel_time': self.current_time,
            'update_time': self.current_time}
        model_update(self.order, data)

        # 站内消息
        content = _(u'您的订单%s已取消。' % self.order.order_sn)
        mcs = MessageCreateService(
            1,
            self.order.uid,
            -1,
            content,
            ttype=1,
            tid=self.order.order_id,
            current_time=self.current_time)
        if not mcs.check():
            log_error('order_id:%s msg:%s' % (self.order.order_id, mcs.msg))
        else:
            mcs.do()

        self.commit()
        return True


class OrderDeliverService(object):
    """确认收货Service"""

    def __init__(self, order_id, uid):
        """初始化函数"""

        self.order_id = order_id                 # 订单ID
        self.uid = uid                           # 用户ID
        self.current_time = current_timestamp()  # 当前时间
        self.order = None                        # 订单实例
        self.__is_check_order = False            # 是否检查订单

    def check(self):
        """检查"""

        if self.__is_check_order:
            return True
        self.__is_check_order = True

        self.order = Order.query.\
            filter(Order.order_id == self.order_id).\
            filter(Order.uid == self.uid).first()
        if self.order is None:
            raise OrderException(_(u'找不到订单'))

        if self.order.shipping_status != 2:
            raise OrderException(_(u'商品还没有发货，不能确认收货'))

        if self.order.deliver_status == 2:
            raise OrderException(_(u'已经确认过发货，请勿重复确认'))

        return True

    def deliver(self):
        """确认收货"""

        try:
            self.check()
        except OrderException as e:
            raise e

        data = {
            'order_status': 2,
            'deliver_status': 2,
            'deliver_time': self.current_time}
        model_update(self.order, data)

        # 站内消息
        content = _(u'您的订单%s已确认签收，请前往评价。' % self.order.order_sn)
        mcs = MessageCreateService(
            1,
            self.order.uid,
            -1,
            content,
            ttype=1,
            tid=self.order.order_id,
            current_time=self.current_time)
        if not mcs.check():
            log_error('order_id:%s msg:%s' % (self.order.order_id, mcs.msg))
        else:
            mcs.do()

        db.session.commit()

        # 微信消息
        WeixinMessageStaticMethodsService.deliver(self.order)


class OrderStaticMethodsService(object):
    """订单静态方法Service"""

    @staticmethod
    def create_order_sn(current_time):
        """创建订单编号"""

        current_time = timestamp2str(current_time, 'YYYYMMDDHHmmss')
        randint = random.randint(1000, 9999)
        order_sn = '%s%s' % (current_time, randint)

        order = Order.query.filter(Order.order_sn == order_sn).first()
        if order:
            order_sn = OrderStaticMethodsService.create_order_sn(current_time)

        return order_sn

    @staticmethod
    def orders(uid, params, is_pagination=False):
        """获取订单列表"""

        p = toint(params.get('p', '1'))
        ps = toint(params.get('ps', '10'))
        # 标签状态: 0.全部; 1.待付款; 2.待收货; 3.已完成; 4.已取消;
        tab_status = toint(params.get('tab_status', '0'))

        q = db.session.query(
            Order.order_id, Order.order_sn, Order.order_status, Order.order_amount,
            Order.pay_status, Order.shipping_amount, Order.shipping_status,
            Order.deliver_status, Order.goods_quantity, Order.goods_data,
            Order.add_time, Order.shipping_time, Order.aftersale_status).\
            filter(Order.uid == uid).\
            filter(Order.order_type == 1).\
            filter(Order.is_remove == 0)

        if tab_status == 1:
            q = q.filter(Order.order_status == 1).filter(Order.pay_status == 1)

        if tab_status == 2:
            q = q.filter(Order.order_status == 1).filter(
                Order.pay_status == 2).filter(Order.deliver_status.in_([0, 1]))

        if tab_status == 3:
            q = q.filter(Order.order_status == 2).filter(
                Order.pay_status == 2).filter(Order.deliver_status == 2)

        if tab_status == 4:
            current_time = current_timestamp()
            min_pay_time = before_after_timestamp(current_time, {'days': 1})

            q = q.filter(or_((Order.add_time >= min_pay_time),
                             (Order.order_status == 3)))

        orders = q.order_by(Order.order_id.desc()).offset(
            (p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        texts = {}
        codes = {}
        aftersales = {}
        for order in orders:
            text, code = OrderStaticMethodsService.order_status_text_and_action_code(
                order)
            texts[order.order_id] = text
            codes[order.order_id] = code
            aftersale = Aftersales.query.\
                filter(Aftersales.order_id == order.order_id).\
                filter(Aftersales.status.in_([1, 2, 3])).first()
            if aftersale:
                aftersales[order.order_id] = aftersale

        return {
            'orders': orders,
            'pagination': pagination,
            'texts': texts,
            'codes': codes,
            'aftersales': aftersales,
            'current_time': current_timestamp()}

    @staticmethod
    def order_status_text_and_action_code(order, min_pay_time=0):
        """获取订单状态和订单指令"""

        status_text = u''   # 订单状态: 已取消; 待付款; 待收货; 待评价; 已完成;
        # 订单指令: 0.无指令; 1.付款; 2.取消订单; 3.查看物流; 4.确认收货; 5.再次购买; 6.删除订单; 7.申请售后; 8.申请退款;
        action_code = []

        current_time = current_timestamp()
        min_pay_time = min_pay_time if min_pay_time else before_after_timestamp(
            current_time, {'days': 1})

        if order.order_status == 1:
            if order.pay_status == 1:
                if order.add_time < min_pay_time:
                    status_text = _(u'待付款')
                    action_code = [1, 2, 5]

                    return (status_text, action_code)

                if order.add_time >= min_pay_time:
                    status_text = _(u'已取消')
                    action_code = [5, 6]

                    return (status_text, action_code)

            if order.pay_status == 2:
                if order.shipping_status == 1:
                    status_text = _(u'待收货')
                    action_code = [5, 8]

                    return (status_text, action_code)

                if order.shipping_status == 2 and order.deliver_status == 1:
                    status_text = _(u'待收货')
                    action_code = [3, 4, 5, 7]

                    return (status_text, action_code)

        if order.order_status == 2:
            status_text = _(u'已完成')
            action_code = [3, 5, 6, 7]

            return (status_text, action_code)

        if order.order_status == 3:
            status_text = _(u'已取消')
            action_code = [5, 6]

            return (status_text, action_code)

        if order.order_status == 4:
            if order.aftersale_status == 1:
                status_text = _(u'已退款')
                action_code = []

                return (status_text, action_code)

            if order.aftersale_status == 2:
                status_text = _(u'已换货')
                action_code = []

                return (status_text, action_code)

            if order.aftersale_status == 3:
                status_text = _(u'已退款，已换货')
                action_code = []

                return (status_text, action_code)

        return (status_text, action_code)

    @staticmethod
    def detail_page(order_id, uid):
        """详情页面"""

        order = Order.query.filter(Order.order_id == order_id).filter(
            Order.uid == uid).first()
        if not order:
            return abort(404)

        items = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
        ogs_aftersale_status = OrderStaticMethodsService.\
            order_goods_aftersale_status(items, order)
        order_address = OrderAddress.query.filter(
            OrderAddress.order_id == order_id).first()
        text, code = OrderStaticMethodsService.\
            order_status_text_and_action_code(order)

        express_data = None
        express_datas = []
        if order.shipping_status == 2:
            try:
                trackservice = TrackServiceFactory.get_trackservice()
                _express_data = trackservice.track(
                    order.shipping_code,
                    order.shipping_sn,
                    order_address.mobile)
                _express_msg = 'ok'
                express_data = _express_data[0] if len(_express_data) > 0 else {}
                express_datas = _express_data
            except ShippingException as e:
                _express_msg = e.msg

        aftersale = Aftersales.query.\
            filter(Aftersales.order_id == order_id).\
            filter(Aftersales.status.in_([1, 2, 3])).first()

        data = {
            'order': order,
            'items': items,
            'ogs_aftersale_status': ogs_aftersale_status,
            'order_address': order_address,
            'text': text, 'code': code,
            'express_data': express_data,
            'express_datas': express_datas,
            'aftersale': aftersale,
            'current_time': current_timestamp()}
        return data

    @staticmethod
    def order_goods_aftersale_status(order_goods, order):
        """订单商品状态"""
        ogs_aftersale_status = {}
        current_time = current_timestamp()
        limit_time = before_after_timestamp(order.shipping_time, {'days': 15})

        for og in order_goods:
            # 申请售后
            if (order.order_status in [1, 2, 4]) and\
                (order.pay_status == 2) and\
                (order.shipping_status == 2) and\
                (limit_time >= current_time) and\
                    (og.goods_quantity > og.aftersales_goods_quantity):
                ogs_aftersale_status[og.og_id] = {
                    'status_code': 1, 'aftersales_id': 0}
                continue

            # 售后处理中
            aftersales_goods = db.session.query(
                    AftersalesGoods.ag_id, Aftersales.aftersales_id).\
                filter(AftersalesGoods.aftersales_id == Aftersales.aftersales_id).\
                filter(AftersalesGoods.og_id == og.og_id).\
                filter(Aftersales.status.in_([1, 2])).first()
            if aftersales_goods:
                ogs_aftersale_status[og.og_id] = {
                    'status_code': 2,
                    'aftersales_id': aftersales_goods.aftersales_id}
                continue

            # 完成售后的状态
            if order.order_status == 4:
                refund_sum = db.session.\
                    query(func.sum(AftersalesGoods.goods_quantity).label('sum')).\
                    filter(AftersalesGoods.aftersales_id == Aftersales.aftersales_id).\
                    filter(AftersalesGoods.og_id == og.og_id).\
                    filter(Aftersales.aftersales_type.in_([1, 2])).\
                    filter(Aftersales.status == 3).first()
                _refund_sum = refund_sum.sum if refund_sum.sum else 0
                if _refund_sum == og.goods_quantity:
                    ogs_aftersale_status[og.og_id] = {
                        'status_code': 3, 'aftersales_id': 0}
                    continue

                exchange_sum = db.session.\
                    query(func.sum(AftersalesGoods.goods_quantity).label('sum')).\
                    filter(AftersalesGoods.aftersales_id == Aftersales.aftersales_id).\
                    filter(AftersalesGoods.og_id == og.og_id).\
                    filter(Aftersales.aftersales_type == 3).\
                    filter(Aftersales.status == 3).first()
                _exchange_sum = exchange_sum.sum if exchange_sum.sum else 0
                if _exchange_sum == og.goods_quantity:
                    ogs_aftersale_status[og.og_id] = {
                        'status_code': 4, 'aftersales_id': 0}
                    continue

                if (_refund_sum + _exchange_sum) == og.goods_quantity:
                    ogs_aftersale_status[og.og_id] = {
                        'status_code': 5, 'aftersales_id': 0}
                    continue

            ogs_aftersale_status[og.og_id] = 0

        return ogs_aftersale_status

    @staticmethod
    def order_comments(uid, params, is_pagination=False):
        """ 订单评价中心 """

        p = toint(params.get('p', '1'))
        ps = toint(params.get('ps', '10'))
        is_pending = toint(params.get('is_pending', '0'))

        completed = db.session.query(Order.order_id).\
            filter(Order.uid == uid).\
            filter(Order.is_remove == 0).\
            filter(Order.order_status == 2).\
            filter(Order.pay_status == 2).\
            filter(Order.deliver_status == 2).all()
        completed = [order.order_id for order in completed]

        q = db.session.query(
            OrderGoods.og_id, OrderGoods.goods_id, OrderGoods.goods_name,
            OrderGoods.goods_img, OrderGoods.goods_desc,
            OrderGoods.goods_price, OrderGoods.comment_id).\
            filter(OrderGoods.order_id.in_(completed))
        pending_count = get_count(q.filter(OrderGoods.comment_id == 0))
        unpending_count = get_count(q.filter(OrderGoods.comment_id > 0))

        if is_pending == 1:
            q = q.filter(OrderGoods.comment_id == 0)
        else:
            q = q.filter(OrderGoods.comment_id > 0)

        comments = None
        pagination = None
        if is_pagination:
            comments = q.order_by(OrderGoods.og_id.desc()).offset(
                (p-1)*ps).limit(ps).all()
            pagination = Pagination(None, p, ps, q.count(), None)
        else:
            comments = q.order_by(OrderGoods.og_id.desc()).all()

        data = {'is_pending': is_pending, 'pending_count': pending_count,
                'unpending_count': unpending_count, 'comments': comments,
                'pagination': pagination}

        return data
