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
    model_create,
    model_update,
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp

from app.models.funds import Funds, FundsDetail


class FundsService(object):
    """ 资金Service """

    def __init__(self, uid, funds_change, event=0, ttype=0, tid=0, remark_user='', remark_sys='', current_time=0):
        self.msg          = u''
        self.uid          = uid
        self.funds_change = funds_change    # 变更资金: 收入即值大于0, 支出即值小于或等于0
        self.event        = event           # 事件: 0.默认; 1.充值; 2.支付; 3.退款;
        self.ttype        = ttype           # 第三方类型: 0.默认; 1.tran; 2.order;
        self.tid          = tid             # 第三方ID
        self.remark_user  = remark_user
        self.remark_sys   = remark_sys
        self.current_time = current_time if current_time else current_timestamp()
        self.funds_obj    = None
        self.funds_detail = None
        self.funds_prev   = Decimal('0.00')
        self.funds        = Decimal('0.00')

    def commit(self):
        """ 提交sql事务 """

        db.session.commit()

    def check(self):
        """ 检查 """

        # 变更资金
        try:
            self.funds_change = Decimal(self.funds_change)
        except Exception as e:
            self.msg = _(u'金额错误')
            return False

        # 用户帐户
        self.funds_obj = Funds.query.filter(Funds.uid == self.uid).first()

        # 检查
        if self.funds_change <= 0:
            if (-self.funds_change) > self.funds_obj.funds:
                self.msg = _(u'余额不足')
                return False

        # 上次余额
        self.funds_prev = Decimal(self.funds_obj.funds)

        # 更改后的余额
        self.funds = self.funds_prev + self.funds_change

        return True

    def update(self):
        """ 更新 """

        # 更新
        model_update(self.funds_obj, {'funds':self.funds, 'update_time':self.current_time})

        # 创建流水
        data = {'uid':self.uid, 'funds_prev':self.funds_prev, 'funds_change':self.funds_change, 'funds':self.funds,
                'event':self.event, 'ttype':self.ttype, 'tid':self.tid, 'remark_user':self.remark_user,
                'remark_sys':self.remark_sys, 'add_time':self.current_time}
        self.funds_detail = model_create(FundsDetail, data)

        return True


class FundsStaticMethodsService(object):
    """资金静态方法Service"""

    @staticmethod
    def details(params):
        """获取资金流水列表"""

        p      = toint(params.get('p', '1'))
        ps     = toint(params.get('ps', '10'))
        uid    = toint(params.get('uid', '0'))

        details = db.session.query(FundsDetail.fd_id, FundsDetail.funds_change, FundsDetail.event, FundsDetail.add_time).\
                        filter(FundsDetail.uid == uid).\
                        order_by(FundsDetail.fd_id.desc()).offset((p-1)*ps).limit(ps).all()

        return details
