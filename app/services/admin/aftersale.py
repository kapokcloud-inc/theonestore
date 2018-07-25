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

from app.services.admin.refunds import RefundsService

from app.models.order import (
    Order,
    OrderGoods,
    OrderAddress
)
from app.models.aftersales import (
    Aftersales,
    AftersalesLogs,
    AftersalesGoods
)


class AfterSaleCheckService(object):
    """售后审核Service"""

    def __init__(self, aftersales_id, check_status, content):
        self.msg              = u''
        self.aftersales_id    = aftersales_id
        self.check_status     = check_status
        self.content          = content
        self.aftersale        = None
        self.aftersale_goods  = None
        self.order_address    = None
        self.order_goods      = None
        self.order_goods_list = []
        self.current_time     = current_timestamp()

    def check(self):
        """检查"""

        # 检查
        if self.aftersales_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.check_status not in [2,3]:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.check_status == 3 and self.content == '':
            self.msg = _(u'请填写拒绝原因')
            return False

        # 检查
        self.aftersale = Aftersales.query.get(self.aftersales_id)
        if not self.aftersale:
            self.msg = _(u'售后不存在')
            return False

        # 检查
        if self.aftersale.status != 1 and self.aftersale.check_status != 1:
            self.msg = _(u'状态错误')
            return False

        # 检查
        if self.aftersale.aftersales_type in [2,3]:
            self.order_address = OrderAddress.query.filter(OrderAddress.order_id == self.aftersale.order_id).first()
            if not self.order_address:
                self.msg = _(u'订单地址不存在')
                return False

        if self.aftersale.aftersales_type == 1:
            self.order_goods_list = OrderGoods.query.filter(OrderGoods.order_id == self.aftersale.order_id).all()
        else:
            self.aftersale_goods = AftersalesGoods.query.filter(AftersalesGoods.aftersales_id == self.aftersales_id).first()
            self.order_goods     = OrderGoods.query.get(self.aftersale_goods.og_id)

        return True

    def do(self):
        """审核"""

        if self.check_status == 2:
            data = {'status':2, 'check_status':2, 'return_status':1, 'update_time':self.current_time}

            content = _(u'您的服务单号：%s审核通过。' % self.aftersale.aftersales_sn)
            if self.aftersale.aftersales_type in [2,3]:
                address = '%s%s%s%s' % (self.order_address.province, self.order_address.city,
                                        self.order_address.district, self.order_address.address)
                name    = self.order_address.name
                mobile  = self.order_address.mobile
                content = '%s地址：%s 收货人：%s 电话：%s' % (content, address, name, mobile)
        else:
            data    = {'status':4, 'check_status':3, 'update_time':self.current_time}
            content = _(u'抱歉通知您，您的服务单号：%s审核不通过。原因：%s' % (self.aftersale.aftersales_sn, self.content))

            # 还原售后商品数量
            if self.aftersale.aftersales_type == 1:
                for order_goods in self.order_goods_list:
                    _data = {'aftersales_goods_quantity':0, 'update_time':self.current_time}
                    model_update(order_goods, _data)
            else:
                aftersales_goods_quantity = self.order_goods.aftersales_goods_quantity - self.aftersale_goods.goods_quantity
                _data = {'aftersales_goods_quantity':aftersales_goods_quantity, 'update_time':self.current_time}
                model_update(self.order_goods, _data)

        model_update(self.aftersale, data)

        AfterSaleStaticMethodsService.add_log(self.aftersales_id, content, self.current_time, commit=True)

        return True


class AfterSaleReceivedService(object):
    """已签收Service"""

    def __init__(self, aftersales_id):
        self.msg           = u''
        self.aftersales_id = aftersales_id
        self.aftersale     = None
        self.current_time  = current_timestamp()

    def check(self):
        """检查"""

        # 检查
        if self.aftersales_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        self.aftersale = Aftersales.query.get(self.aftersales_id)
        if not self.aftersale:
            self.msg = _(u'售后不存在')
            return False

        # 检查
        if self.aftersale.aftersales_type not in [2,3]:
            self.msg = _(u'售后类型错误')
            return False

        # 检查
        if self.aftersale.status != 2 and self.aftersale.return_status != 2:
            self.msg = _(u'状态错误')
            return False

        return True

    def do(self):
        """已签收"""

        data = {'return_status':3, 'update_time':self.current_time}

        if self.aftersale.aftersales_type == 3:
            data['resend_status'] = 1

        model_update(self.aftersale, data)

        content = _(u'退货/换货商品已抵达，需要1-3个工作日处理，请耐心等待。')
        AfterSaleStaticMethodsService.add_log(self.aftersales_id, content, self.current_time, commit=True)

        return True


class AfterSaleResendService(object):
    """重发商品Service"""

    def __init__(self, aftersales_id, resend_shipping_name, resend_shipping_sn):
        self.msg                  = u''
        self.aftersales_id        = aftersales_id
        self.resend_shipping_name = resend_shipping_name
        self.resend_shipping_sn   = resend_shipping_sn
        self.aftersale            = None
        self.current_time         = current_timestamp()

    def check(self):
        """检查"""

        # 检查
        if self.aftersales_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        if self.resend_shipping_name == '':
            self.msg = _(u'快递名称')
            return False

        # 检查
        if self.resend_shipping_sn == '':
            self.msg = _(u'快递单号')
            return False

        # 检查
        self.aftersale = Aftersales.query.get(self.aftersales_id)
        if not self.aftersale:
            self.msg = _(u'售后不存在')
            return False

        # 检查
        if self.aftersale.aftersales_type != 3:
            self.msg = _(u'售后类型错误')
            return False

        # 检查
        if self.aftersale.status != 2 and self.aftersale.return_status != 3 and self.aftersale.resend_status != 1:
            self.msg = _(u'状态错误')
            return False

        return True

    def do(self):
        """重发商品"""

        data = {'resend_status':2, 'update_time':self.current_time}
        model_update(self.aftersale, data)

        content = _(u'服务专员已处理换货，包裹已发出，%s，快递单号:%s，请注意查收。' % (self.resend_shipping_name, self.resend_shipping_sn))
        AfterSaleStaticMethodsService.add_log(self.aftersales_id, content, self.current_time, commit=True)

        return True


class AfterSaleRefundsService(object):
    """退款Service"""

    def __init__(self, aftersales_id):
        self.msg           = u''
        self.aftersales_id = aftersales_id
        self.pay_methods   = ['funds', 'weixin_jsapi']
        self.aftersale     = None
        self.order         = None
        self.rs            = None
        self.current_time  = current_timestamp()

    def check(self):
        """检查"""

        # 检查
        if self.aftersales_id <= 0:
            self.msg = _(u'参数错误')
            return False

        # 检查
        self.aftersale = Aftersales.query.get(self.aftersales_id)
        if not self.aftersale:
            self.msg = _(u'售后不存在')
            return False

        # 检查
        if self.aftersale.aftersales_type not in [1,2]:
            self.msg = _(u'售后类型错误')
            return False

        # 检查
        if self.aftersale.aftersales_type == 1 and self.aftersale.status != 1 and self.aftersale.check_status != 1:
            self.msg = _(u'状态错误')
            return False

        # 检查
        if self.aftersale.aftersales_type == 2 and self.aftersale.status != 2 and self.aftersale.return_status != 3:
            self.msg = _(u'状态错误')
            return False

        # 检查
        self.order = Order.query.get(self.aftersale.order_id)
        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        # 检查
        if self.order.pay_method not in self.pay_methods:
            self.msg = _(u'订单支付方式错误')
            return False

        # 检查
        self.rs = RefundsService(self.aftersale.order_id, self.aftersale.refunds_amount, self.current_time)
        if not self.rs.check():
            self.msg = self.rs.msg
            return False

        return True

    def do(self):
        """退款"""

        self.rs.do()
        if self.rs.refunds.refunds_status == 1:
            if self.aftersale.aftersales_type == 1:
                data = {'status':3, 'check_status':2, 'refunds_method':self.rs.refunds.refunds_method,
                        'refunds_sn':self.rs.refunds.refunds_sn, 'refunds_status':2, 'update_time':self.current_time}

                # 余额退款
                if self.order.pay_method == 'funds':
                    content = _(u'您的服务单号：%s审核通过，退款金额已经到钱包，请注意查收。' % self.aftersale.aftersales_sn)

                # 微信退款
                if self.order.pay_method == 'weixin_jsapi':
                    content = _(u'您的服务单号:%s审核通过，退款到帐可能需要1-3个工作日到帐，请注意查收帐号。' % self.aftersale.aftersales_sn)
            else:
                data    = {'status':3, 'refunds_method':self.rs.refunds.refunds_method,
                            'refunds_sn':self.rs.refunds.refunds_sn, 'refunds_status':2, 'update_time':self.current_time}
                content = _(u'服务专员已处理退款，退款金额已经到钱包，请注意查收。')

            data['refunds_sn'] = self.rs.refunds.refunds_sn
            model_update(self.aftersale, data)
            AfterSaleStaticMethodsService.add_log(self.aftersales_id, content, self.current_time, commit=True)

        return True


class AfterSaleStaticMethodsService(object):
    """售后静态方法Service"""


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
        """获取售后状态和售后指令"""

        status_text = u''
        action_code = []    # 售后指令列表: 1.审核通过; 2.拒绝通过; 3.收到寄回商品; 4.重发换货商品; 5.退款;

        if aftersale.aftersales_type == 1:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')
                action_code = [2,5]

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 3 and aftersale.check_status == 2 and aftersale.refunds_status == 2:
                status_text = _(u'退款成功，已完成')

        if aftersale.aftersales_type == 2:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')
                action_code = [1,2]

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 2 and aftersale.check_status == 2 and aftersale.return_status == 1:
                status_text = _(u'审核通过，待寄退货商品')

            if aftersale.status == 2 and aftersale.return_status == 2:
                status_text = _(u'已寄退货商品，待收件')
                action_code = [3]

            if aftersale.status == 2 and aftersale.return_status == 3:
                status_text = _(u'已收到退货商品，待退款')
                action_code = [5]

            if aftersale.status == 3 and aftersale.refunds_status == 2:
                status_text = _(u'退款成功，已完成')

        if aftersale.aftersales_type == 3:
            if aftersale.status == 1 and aftersale.check_status == 1:
                status_text = _(u'等待审核')
                action_code = [1,2]

            if aftersale.status == 4 and aftersale.check_status == 3:
                status_text = _(u'审核不通过')

            if aftersale.status == 2 and aftersale.check_status == 2 and aftersale.return_status == 1:
                status_text = _(u'审核通过，待寄换货商品')

            if aftersale.status == 2 and aftersale.return_status == 2:
                status_text = _(u'已寄换货商品，待收件')
                action_code = [3]

            if aftersale.status == 2 and aftersale.return_status == 3 and aftersale.resend_status == 1:
                status_text = _(u'已收到换货商品，待处理')
                action_code = [4]

            if aftersale.status in [2,3] and aftersale.resend_status in [2,3]:
                status_text = _(u'重新发货，已完成')

        return (status_text, action_code)
