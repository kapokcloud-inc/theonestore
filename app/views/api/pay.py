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
    Blueprint,
    request
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp

from app.services.response import ResponseJson
from app.services.api.order import PayService, PaidService
from app.services.api.funds import FundsService


pay = Blueprint('api.pay', __name__)

resjson = ResponseJson()
resjson.module_code = 15

@pay.route('/fundspay/req')
def fundspay_req():
    """ 余额支付请求 """
    resjson.action_code = 10

    # ??
    #if not check_login():
    #    return resjson.print_json(10, _(u'未登陆'))
    #uid = get_uid()
    uid = 1

    paid_time  = current_timestamp()
    pay_amount = Decimal('0.00')

    args          = request.args
    order_id_list = args.get('order_id_list', '[]').strip()
    try:
        order_id_list = json.loads(order_id_list)
    except Exception, e:
        return resjson.print_json(10, _(u'支付订单ID列表数据格式错误'))

    ps = PayService(uid, order_id_list)
    if not ps.check():
        return resjson.print_json(11, ps.msg)

    if not ps.tran:
        ps.create_tran()

    tran        = ps.tran
    tran_id     = tran.tran_id
    pay_amount -= Decimal(tran.pay_amount)

    # 更新资金 - 使用资金支付 - 检查
    remark_user = _(u'支付订单')
    remark_sys  = _(u'支付订单，交易ID:%s 支付金额:%s' % (tran_id, pay_amount))
    fs = FundsService(uid, pay_amount, 1, 1, tran_id, remark_user, remark_sys, paid_time)
    if not fs.check():
        return resjson.print_json(12, fs.msg)

    # 更新资金 - 使用资金支付 - 支付
    fs.update()

    data = {'pay_tran_id':fs.funds_detail.fd_id, 'pay_method':'funds',
            'paid_time':paid_time, 'paid_amount':fs.funds_change}
    ps   = PaidService(tran_id, **data)

    log_info("[InfoViewApiPayFundspayReq] tran_id:%s paid_amount: %s" % (tran_id, fs.funds_change))

    ps.paid()

    return resjson.print_json(0, u'ok', {'info':{}, 'tran':tran})
