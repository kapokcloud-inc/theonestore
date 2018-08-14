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
from flask_sqlalchemy import Pagination
from sqlalchemy import func

from app.database import db

from app.helpers import (
    log_info,
    toint,
    model_to_dict_only,
    model_create,
    model_update,
    model_delete
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str,
    before_after_timestamp
)

from app.forms.api.aftersales import AfterSalesAddressForm

from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods
)
from app.models.aftersales import (
    Aftersales,
    AftersalesAddress,
    AftersalesLogs,
    AftersalesGoods
)


class AfterSalesCreateService(object):
    """创建售后Service"""

    def __init__(self, uid, order_id=0, og_id=0, quantity=0, aftersales_type=0, deliver_status=0, content='', img_data='[]'):
        self.msg              = u''
        self.uid              = uid                     # 用户UID
        self.order_id         = toint(order_id)         # 订单ID
        self.og_id            = toint(og_id)            # 订单商品ID
        self.quantity         = toint(quantity)         # 售后商品数量
        self.aftersales_type  = toint(aftersales_type)  # 售后类型: 0.默认; 1.仅退款; 2.退货退款; 3.仅换货;
        self.deliver_status   = toint(deliver_status)   # 订单收货状态: 0.默认; 1.未收货; 2.已收货;
        self.content          = content                 # 申请原因
        self.img_data         = img_data                # 图片数据
        self.current_time     = current_timestamp()     # 当前时间
        self.refunds_amount   = Decimal('0.00')         # 退款金额
        self.goods_data       = []                      # 售后商品数据
        self.order            = None                    # 订单实例
        self.order_address    = None                    # 收货地址实例
        self.order_goods      = None                    # 订单商品实例
        self.order_goods_list = []                      # 订单商品实例列表
        self.address_data     = {}                      # 售后地址数据

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
    
        limit_time = before_after_timestamp(self.order.paid_time, {'days':7})
        if self.current_time >= limit_time:
            self.msg = _(u'超过有效退款时间')
            return False

        aftersales = Aftersales.query.filter(Aftersales.order_id == self.order_id).filter(Aftersales.status.in_([1,2,3])).first()
        if aftersales:
            self.msg = _(u'售后状态错误')
            return False

        only                  = ['og_id', 'goods_id', 'goods_name', 'goods_img', 'goods_desc', 'goods_quantity']
        self.order_goods_list = OrderGoods.query.filter(OrderGoods.order_id == self.order_id).all()
        for order_goods in self.order_goods_list:
            _goods_data = model_to_dict_only(order_goods, only)
            self.goods_data.append(_goods_data)

        self.refunds_amount = AfterSalesStaticMethodsService.refunds_amount(order=self.order)

        _sum          = db.session.query(func.sum(OrderGoods.goods_quantity).label('goods_sum')).\
                            filter(OrderGoods.order_id == self.order_id).first()
        self.quantity = _sum.goods_sum

        self.order_address = OrderAddress.query.filter(OrderAddress.order_id == self.order_id).first()

        return True

    def _check_order_goods(self):
        """检查订单商品"""

        if self.quantity <= 0:
            self.msg = _(u'参数错误')
            return False

        if self.aftersales_type not in [2,3]:
            self.msg = _(u'类型错误')
            return False

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

        if self.order.order_status not in [1,2]:
            self.msg = _(u'订单状态错误')
            return False

        if self.order.pay_status != 2:
            self.msg = _(u'支付状态错误')
            return False

        if self.order.shipping_status != 2:
            self.msg = _(u'发货状态错误')
            return False

        maximum = AfterSalesStaticMethodsService.maximum(self.order_goods)
        if self.quantity > maximum:
            self.msg = _(u'数量错误')
            return False

        if self.aftersales_type == 2:
            limit_time = before_after_timestamp(self.order.paid_time, {'days':7})
            if self.current_time >= limit_time:
                self.msg = _(u'超过有效退款时间')
                return False

            self.refunds_amount = AfterSalesStaticMethodsService.refunds_amount(
                                                                    order_goods=self.order_goods,
                                                                    quantity=self.quantity)

        if self.aftersales_type == 3:
            limit_time = before_after_timestamp(self.order.shipping_time, {'days':15})
            if self.current_time >= limit_time:
                self.msg = _(u'超过有效换货时间')
                return False

        self.order_address = OrderAddress.query.filter(OrderAddress.order_id == self.order.order_id).first()

        data = {'og_id':self.order_goods.og_id, 'goods_id':self.order_goods.goods_id,
                'goods_name':self.order_goods.goods_name, 'goods_img':self.order_goods.goods_img,
                'goods_desc':self.order_goods.goods_desc, 'goods_quantity':self.quantity, 'maximum':maximum}
        self.goods_data.append(data)

        return True

    def __check_address(self):
        """检查售后地址"""

        wtf_form = AfterSalesAddressForm()
        if not wtf_form.validate_on_submit():
            for key,value in wtf_form.errors.items():
                self.msg = value[0]
            return False

        self.address_data = {'name':wtf_form.name.data, 'mobile':wtf_form.mobile.data,
                            'province':wtf_form.province.data, 'city':wtf_form.city.data,
                            'district':wtf_form.district.data, 'address':wtf_form.address.data,
                            'add_time':self.current_time, 'update_time':self.current_time}

        return True

    def check(self):
        """检查"""

        # 检查
        if self.order_id <= 0 and self.og_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.aftersales_type not in [0,1,2,3]:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.deliver_status not in [0,1,2]:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.aftersales_type == 1:
            if self.og_id > 0 and self.deliver_status == 0:
                self.msg = _(u'请选择货物状态')
                return False
        else:
            self.deliver_status = 2

        # 检查
        if not self.content:
            self.msg = _(u'请填写申请原因')
            return False

        # 检查
        if self.order_id > 0:
            if not self._check_order():
                return False

        # 检查
        if self.og_id > 0:
            if not self._check_order_goods():
                return False

            if not self.__check_address():
                return False

        return True

    def create(self):
        """创建"""

        aftersales_sn = AfterSalesStaticMethodsService.create_aftersales_sn(self.current_time)

        for data in self.goods_data:
            if self.og_id > 0:
                data.pop('maximum')
        goods_data = json.dumps(self.goods_data)

        data      = {'aftersales_sn':aftersales_sn, 'uid':self.uid, 'order_id':self.order.order_id,
                    'aftersales_type':self.aftersales_type, 'deliver_status':self.deliver_status, 'content':self.content,
                    'img_data':self.img_data, 'status':1, 'check_status':1, 'refunds_amount':self.refunds_amount,
                    'refunds_method':self.order.pay_method, 'latest_log':u'',
                    'goods_data':goods_data, 'quantity':self.quantity,
                    'add_time':self.current_time, 'update_time':self.current_time}
        aftersales = model_create(Aftersales, data, commit=True)

        for data in self.goods_data:
            data['aftersales_id'] = aftersales.aftersales_id
            model_create(AftersalesGoods, data)

        # 售后商品数量 - 单个
        if self.order_goods:
            quantity = self.order_goods.aftersales_goods_quantity + self.quantity
            data     = {'aftersales_goods_quantity':quantity, 'update_time':self.current_time}
            model_update(self.order_goods, data)
    
        # 售后商品数量 - 整单
        if len(self.order_goods_list) > 0:
            for order_goods in self.order_goods_list:
                data = {'aftersales_goods_quantity':order_goods.goods_quantity, 'update_time':self.current_time}
                model_update(order_goods, data)
        
        AfterSalesStaticMethodsService.add_log(aftersales.aftersales_id, _(u'申请售后服务，等待商家审核。'), self.current_time, False)

        # 售后地址
        if self.address_data:
            self.address_data['aftersales_id'] = aftersales.aftersales_id
            model_create(AftersalesAddress, self.address_data)

        db.session.commit()

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
    def aftersales(params, is_pagination=False):
        """获取售后列表"""

        p   = toint(params.get('p', '1'))
        ps  = toint(params.get('ps', '10'))
        uid = toint(params.get('uid', '0'))

        q          = Aftersales.query.filter(Aftersales.uid == uid)
        aftersales = q.order_by(Aftersales.aftersales_id.desc()).offset((p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        return {'aftersales':aftersales, 'pagination':pagination}

    @staticmethod
    def maximum(order_goods):
        """最大售后商品数量"""

        maximum = order_goods.goods_quantity - order_goods.aftersales_goods_quantity

        """
        aftersales    = db.session.query(Aftersales.aftersales_id).\
                            filter(Aftersales.order_id == order_goods.order_id).\
                            filter(Aftersales.status.in_([1,2,3])).all()
        aftersales_id = [aftersale.aftersales_id for aftersale in aftersales]

        _sum      =  db.session.query(func.sum(AftersalesGoods.goods_quantity).label('goods_sum')).\
                        filter(AftersalesGoods.aftersales_id.in_(aftersales_id)).first()
        goods_sum = _sum.goods_sum if _sum.goods_sum else 0
        maximum   = order_goods.goods_quantity - goods_sum
        """

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
            # 本订单统计有效的售后ID
            order         = Order.query.filter(Order.order_id == order_goods.order_id).first()
            aftersales    = Aftersales.query.\
                                filter(Aftersales.order_id == order_goods.order_id).\
                                filter(Aftersales.status.in_([1,2,3])).all()
            aftersales_id = [aftersale.aftersales_id for aftersale in aftersales]

            # 本订单统计有效的售后商品总数
            _sum      = db.session.query(func.sum(AftersalesGoods.goods_quantity).label('goods_sum')).\
                                filter(AftersalesGoods.aftersales_id.in_(aftersales_id)).first()
            goods_sum = _sum.goods_sum if _sum.goods_sum else 0

            # 是否最后一次售后
            if (order.goods_quantity - goods_sum) == quantity:
                amount_sum     = db.session.query(func.sum(Aftersales.refunds_amount).label('amount_sum')).\
                                        filter(Aftersales.aftersales_id.in_(aftersales_id)).first()
                amount_sum     = Decimal(amount_sum.amount_sum) if amount_sum.amount_sum else Decimal('0.00')
                refunds_amount = Decimal(order.paid_amount) - Decimal(order.shipping_amount) - amount_sum
            else:
                avg_amount     = Decimal(order.discount_amount) / order.goods_quantity
                refunds_amount = (Decimal(order_goods.goods_price) - avg_amount) * quantity
                refunds_amount = refunds_amount.quantize(Decimal('0.00'))

        return refunds_amount

    @staticmethod
    def add_log(aftersales_id, content, current_time=0, commit=True):
        """添加日志"""

        current_time = current_time if current_time else current_timestamp()

        aftersales = Aftersales.query.get(aftersales_id)
        if aftersales:
            data = {'aftersales_id':aftersales_id, 'content':content, 'add_time':current_time}
            model_create(AftersalesLogs, data)

            data = {'latest_log':content, 'update_time':current_time}
            model_update(aftersales, data, commit=commit)

        return True

    @staticmethod
    def aftersale_status_text_and_action_code(aftersale):
        """获取售后状态"""

        status_text = u''
        action_code = []    # 售后指令列表: 1.寄回商品; 2.签收商品;

        if aftersale.aftersales_type == 1:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 3 and aftersale.check_status == 2 and aftersale.refunds_status == 2:
                status_text = _(u'退款成功，已完成')

        if aftersale.aftersales_type == 2:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 2 and aftersale.check_status == 2 and aftersale.return_status == 1:
                status_text = _(u'审核通过，待寄退货商品')
                action_code = [1]

            if aftersale.status == 2 and aftersale.return_status == 2:
                status_text = _(u'已寄退货商品，待收件')

            if aftersale.status == 2 and aftersale.return_status == 3:
                status_text = _(u'已收到退货商品，待退款')

            if aftersale.status == 3 and aftersale.refunds_status == 2:
                status_text = _(u'退款成功，已完成')

        if aftersale.aftersales_type == 3:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 2 and aftersale.check_status == 2 and aftersale.return_status == 1:
                status_text = _(u'审核通过，待寄换货商品')
                action_code = [1]

            if aftersale.status == 2 and aftersale.return_status == 2:
                status_text = _(u'已寄换货商品，待收件')

            if aftersale.status == 2 and aftersale.return_status == 3 and aftersale.resend_status == 1:
                status_text = _(u'已收到换货商品，待处理')

            if aftersale.status in [2] and aftersale.resend_status in [2]:
                status_text = _(u'重新发货，已完成')
                action_code = [2]

            if aftersale.status in [3] and aftersale.resend_status in [3]:
                status_text = _(u'重新发货，已完成')

        return (status_text, action_code)
