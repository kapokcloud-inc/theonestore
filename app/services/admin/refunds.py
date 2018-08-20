# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask_babel import gettext as _
from sqlalchemy import func

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
    before_after_timestamp,
)

from app.services.api.funds import FundsService
from app.services.admin.pay_weixin import JsapiWeixinRefundsService

from app.models.order import (
    Order,
    OrderTran
)
from app.models.refunds import Refunds


class RefundsService(object):
    """退款Service"""

    def __init__(self, order_id, refunds_amount, current_time=0):
        self.msg            = u''
        self.order_id       = order_id
        self.refunds_amount = refunds_amount
        self.current_time   = current_time if current_time else current_timestamp()
        self.third_type     = 0
        self.fs             = None
        self.jwrs           = None
        self.order          = None
        self.refunds        = None

    def check(self):
        """检查"""

        # 检查
        self.order = Order.query.get(self.order_id)
        if not self.order:
            self.msg = _(u'订单不存在')
            return False

        # 检查
        if self.order.pay_status != 2:
            self.msg = _(u'未支付订单')
            return False

        # 检查
        if self.order.pay_method == 'funds':
            self.third_type = 1
        if self.order.pay_method in ['weixin_app', 'weixin_jsapi']:
            self.third_type = 2
        if self.third_type == 0:
            self.msg = _(u'支付方式错误')
            return False

        # 检查
        refunds_amount_sum = db.session.query(func.sum(Refunds.refunds_amount).label('sum')).\
                                    filter(Refunds.tran_id == self.order.tran_id).\
                                    filter(Refunds.refunds_status == 1).first()
        _sum  = refunds_amount_sum.sum if refunds_amount_sum.sum else 0
        total = _sum + self.refunds_amount
        tran  = OrderTran.query.get(self.order.tran_id)
        if total > tran.pay_amount:
            self.msg = _(u'退款金额超过交易已付金额')
            return False

        # 检查
        if self.third_type == 1:
            remark_user = u'退款'
            remark_sys  = u'退款，订单编号:%s，退款金额:%s' % (self.order.order_sn, self.refunds_amount)
            self.fs     = FundsService(self.order.uid, self.refunds_amount, 3, 2, self.order_id,
                                        remark_user, remark_sys, self.current_time)
            if not self.fs.check():
                self.msg = self.fs.msg
                return False

        # 检查
        if self.third_type == 2:
            after_year_time = before_after_timestamp(self.order.paid_time, {'years':1})
            if self.current_time > after_year_time:
                self.msg = _(u'交易时间超过一年的订单无法提交退款')
                return False

            self.jwrs = JsapiWeixinRefundsService(self.order.tran_id, self.refunds)
            if not self.jwrs.check():
                self.msg = self.jwrs.msg
                return False

        return True

    def do(self):
        """退款"""
        refunds_status = 0  # 退款状态: 0.默认; 1.成功; 2.失败;
        refunds_sn     = ''

        # 是否创建退款记录
        if not self.refunds:
            data = {'tran_id':self.order.tran_id, 'order_id':self.order_id, 'refunds_amount':self.refunds_amount,
                    'refunds_method':self.order.pay_method, 'refunds_sn':'', 'refunds_time':0, 'refunds_status':0,
                    'remark_user':u'', 'remark_sys':u'', 'add_time':self.current_time}
            self.refunds = model_create(Refunds, data)

        # 资金支付
        if self.third_type == 1:
            self.fs.update()
            self.fs.commit()

            refunds_status = 1
            refunds_sn     = self.fs.funds_detail.fd_id

        # 微信
        if self.third_type == 2:
            # 是否退款成功
            if self.jwrs.refunds():
                refunds_status = 1
                refunds_sn     = self.jwrs.refund_id
            else:
                refunds_status = 2

        data = {'refunds_status':refunds_status}
        if refunds_status == 1:
            data = {'refunds_sn':refunds_sn, 'refunds_time':self.current_time, 'refunds_status':refunds_status}

        model_update(self.refunds, data, commit=True)

        return True
