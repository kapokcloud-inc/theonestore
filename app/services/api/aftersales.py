# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import random
import json
from decimal import Decimal

from flask_babel import gettext as _
from sqlalchemy import func

from app.database import db

from app.helpers import (
    log_info,
    toint,
    ktl_to_dl,
    model_create,
    model_update,
    model_delete
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str
)

from app.models.order import (
    Order,
    OrderGoods
)
from app.models.aftersales import (
    Aftersales,
    AftersalesLogs,
    AftersalesGoods
)


class AfterSalesCreateService(object):
    """创建售后Service"""

    def __init__(self, uid, order_id=0, og_id=0, quantity=0, aftersales_type=0, deliver_status=0, content='', img_data='[]'):
        self.msg             = u''
        self.uid             = uid                  # 用户UID
        self.order_id        = order_id             # 订单ID
        self.og_id           = og_id                # 订单商品ID
        self.quantity        = quantity             # 售后商品数量
        self.aftersales_type = aftersales_type      # 售后类型
        self.deliver_status  = deliver_status       # 订单收货状态
        self.content         = content              # 申请原因
        self.img_data        = img_data             # 图片数据
        self.maximum         = 0                    # 最大售后商品数量
        self.refunds_amount  = Decimal('0.00')      # 退款金额
        self.goods_data      = []                   # 售后商品数据
        self.order           = None                 # 订单实例
        self.order_goods     = None                 # 订单商品实例
        self.current_time    = current_timestamp()  #

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def _check_order(self):
        """检查订单"""

        self.order = Order.query.filter(Order.order_id == self.order_id).filter(Order.uid == self.uid).first()
        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        if self.order.order_type != 1:
            self.msg = _(u'订单类型错误')
            return False

        if self.order.order_status != 1:
            self.msg = _(u'订单状态错误')
            return False

        if self.order.pay_status != 2:
            self.msg = _(u'支付状态错误')
            return False

        if self.order.shipping_status != 1:
            self.msg = _(u'发货状态错误')
            return False

        aftersales = Aftersales.query.filter(Aftersales.order_id == self.order_id).filter(Aftersales.status.in_([1,2,3])).first()
        if aftersales:
            self.msg = _(u'售后状态错误')
            return False

        self.goods_data = db.session.query(OrderGoods.og_id, OrderGoods.goods_id, OrderGoods.goods_name, OrderGoods.goods_img,
                                            OrderGoods.goods_desc, OrderGoods.goods_quantity).\
                            filter(OrderGoods.order_id == self.order_id).all()
        self.goods_data = ktl_to_dl(self.goods_data)

        self.refunds_amount = AfterSalesStaticMethodsService.refunds_amount(order=self.order)

        _sum          = db.session.query(func.sum(OrderGoods.goods_quantity).label('goods_sum')).\
                            filter(OrderGoods.order_id == self.order_id).first()
        self.quantity = _sum.goods_sum

        return True

    def _check_order_goods(self):
        """检查订单商品"""

        self.order_goods = OrderGoods.query.get(self.og_id)
        if not self.order_goods:
            self.msg = _(u'订单商品不存在')
            return False

        self.order = Order.query.filter(Order.order_id == self.order_goods.order_id).filter(Order.uid == self.uid).first()
        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        if self.order.order_type != 1:
            self.msg = _(u'订单类型错误')
            return False

        self.maximum = AfterSalesStaticMethodsService.maximum(self.order_goods)
        if self.quantity > self.maximum:
            self.msg = _(u'数量错误')
            return False

        data = {'og_id':self.order_goods.og_id, 'goods_id':self.order_goods.goods_id,
                'goods_name':self.order_goods.goods_name, 'goods_img':self.order_goods.goods_img,
                'goods_desc':self.order_goods.goods_desc, 'goods_quantity':self.order_goods.goods_quantity, 'maximum':self.maximum}
        self.goods_data.append(data)

        self.refunds_amount = AfterSalesStaticMethodsService.refunds_amount(order_goods=self.order_goods, quantity=self.quantity)

        return True
    
    def _check_img_data(self):
        """检查图片数据 ??"""

        return True

    def check(self):
        """检查"""

        # 检查
        if self.order_id <= 0 and self.og_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if not self.content:
            self.msg = _(u'请填写申请原因')
            return False

        if self.order_id > 0:
            if not self._check_order():
                return False

        if self.og_id > 0:
            if not self._check_order_goods():
                return False

        return True

    def create(self):
        """创建"""

        aftersales_sn = AfterSalesStaticMethodsService.create_aftersales_sn(self.current_time)
        goods_data    = json.dumps(self.goods_data)

        data = {'aftersales_sn':aftersales_sn, 'uid':self.uid, 'order_id':self.order.order_id,
                'aftersales_type':self.aftersales_type, 'deliver_status':self.deliver_status, 'content':self.content,
                'img_data':self.img_data, 'status':1, 'check_status':1, 'refunds_amount':self.refunds_amount,
                'refunds_method':self.order.pay_method, 'latest_log':u'',
                'goods_data':goods_data, 'quantity':self.quantity, 'add_time':self.current_time, 'update_time':self.current_time}
        model_create(Aftersales, data)

        return True


class AfterSalesStaticMethodsService(object):
    """售后静态方法Service"""

    @staticmethod
    def create_aftersales_sn(current_time):
        """创建售后编号"""

        current_time  = timestamp2str(current_time, 'YYYYMMDDHHmmss')
        randint       = random.randint(1000, 9999)
        aftersales_sn = '%s%s' % (current_time, randint)

        aftersales = Aftersales.query.filter(Aftersales.aftersales_sn == aftersales_sn).first()
        if aftersales:
            aftersales_sn = AfterSalesStaticMethodsService.create_aftersales_sn(current_time)

        return aftersales_sn

    @staticmethod
    def aftersales(params):
        """获取售后列表"""

        p   = toint(params.get('p', '1'))
        ps  = toint(params.get('ps', '10'))
        uid = toint(params.get('uid', '0'))

        aftersales = db.session.query(Aftersales.aftersales_id, Aftersales.add_time).\
                            filter(Aftersales.uid == uid).\
                            order_by(Aftersales.aftersales_id.desc()).offset((p-1)*ps).limit(ps).all()

        return aftersales

    @staticmethod
    def maximum(order_goods):
        """最大售后商品数量"""

        #maximum = order_goods.goods_quantity - order_goods.service_goods_quantity

        aftersales    = db.session.query(Aftersales.aftersales_id).\
                            filter(Aftersales.order_id == order_goods.order_id).\
                            filter(Aftersales.status.in_([1,2,3])).all()
        aftersales_id = [aftersale.aftersales_id for aftersale in aftersales]

        _sum      =  db.session.query(func.sum(AftersalesGoods.goods_quantity).label('goods_sum')).\
                        filter(AftersalesGoods.aftersales_id.in_(aftersales_id)).first()
        goods_sum = _sum.goods_sum if _sum.goods_sum else 0
        maximum   = order_goods.goods_quantity - goods_sum

        return maximum

    @staticmethod
    def refunds_amount(order=None, order_goods=None, quantity=0):
        """退款金额"""

        refunds_amount = Decimal('0.00')

        # 全单退
        if order:
            refunds_amount = order.paid_amount

        # 部分退
        if order_goods:
            order         = db.session.query(Order.goods_quantity, Order.discount_amount, Order.shipping_amount).\
                                filter(Order.order_id == order_goods.order_id).first()
            aftersales    = db.session.query(Aftersales.aftersales_id).\
                                filter(Aftersales.order_id == order_goods.order_id).\
                                filter(Aftersales.status.in_([1,2,3])).all()
            aftersales_id = [aftersale.aftersales_id for aftersale in aftersales]

            _sum      = db.session.query(func.sum(AftersalesGoods.goods_quantity).label('goods_sum')).\
                                filter(AftersalesGoods.aftersales_id.in_(aftersales_id)).first()
            goods_sum = _sum.goods_sum if _sum.goods_sum else 0

            if (order.goods_quantity - goods_sum) == quantity:
                amount_sum     = db.session.query(func.sum(Aftersales.refunds_amount).label('amount_sum')).\
                                        filter(Aftersales.aftersales_id.in_(aftersales_id)).first()
                refunds_amount = order.paid_amount - amount_sum.amount_sum
            else:
                avg_amount     = (order.discount_amount + order.shipping_amount) / order.goods_quantity
                refunds_amount = round((order_goods.goods_price - avg_amount) * quantity, 2)

        return refunds_amount
