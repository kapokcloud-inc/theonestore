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
    request,
    url_for
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.response import ResponseJson
from app.services.api.order import (
    PayService,
    PaidService
)
from app.services.api.funds import FundsService
from app.services.api.pay_weixin import (
    JsapiOpenidService,
    JsapiPayParamsService,
    JsapiNotifyService
)


pay = Blueprint('api.pay', __name__)

resjson = ResponseJson()
resjson.module_code = 15

@pay.route('/fundspay-req')
def fundspay_req():
    """ 余额支付请求 """
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    paid_time  = current_timestamp()
    pay_amount = Decimal('0.00')

    args          = request.args
    order_id_list = args.get('order_id_list', '[]').strip()
    try:
        order_id_list = json.loads(order_id_list)
    except Exception as e:
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
    fs = FundsService(uid, pay_amount, 2, 1, tran_id, remark_user, remark_sys, paid_time)
    if not fs.check():
        return resjson.print_json(12, fs.msg)

    # 更新资金 - 使用资金支付 - 支付
    fs.update()

    data = {'pay_tran_id':fs.funds_detail.fd_id, 'pay_method':'funds', 'paid_time':paid_time, 'paid_amount':fs.funds_change}
    ps   = PaidService(tran_id, **data)
    ps.paid()

    return resjson.print_json(0, u'ok', {'info':{}, 'tran':tran})


@pay.route('/weixinjspay-openid')
def weixinjspay_openid():
    """获取微信支付openid"""
    resjson.action_code = 11

    order_id      = toint(request.args.get('order_id'))
    redirect_type = toint(request.args.get('redirect_type'))    # 跳转类型: 1.checkout order; 2.funds order;

    if order_id <= 0 or redirect_type not in [1,2]:
        return resjson.print_json(resjson.PARAM_ERROR)

    redirect_uri_dict = {1:url_for('mobile.cart.checkout', order_id=order_id, is_weixin=1), 2:''}    # 2 ??
    redirect_uri      = redirect_uri_dict.get(redirect_type)

    jos = JsapiOpenidService(redirect_uri)
    if not jos.check():
        return resjson.print_json(10, jos.msg)

    openid = jos.openid

    return resjson.print_json(0, u'ok', {'openid':openid})


@pay.route('/weixinjspay-req')
def weixinjspay_req():
    """微信jsapi支付请求"""
    resjson.action_code = 12

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    args          = request.args
    order_id_list = args.get('order_id_list', '[]').strip()
    try:
        order_id_list = json.loads(order_id_list)
    except Exception as e:
        return resjson.print_json(11, _(u'支付订单ID列表数据格式错误'))

    ps = PayService(uid, order_id_list)
    if not ps.check():
        return resjson.print_json(11, ps.msg)

    if not ps.tran:
        ps.create_tran()

    tran      = ps.tran
    subject   = u'交易号：%d' % tran.tran_id
    nonce_str = str(tran.tran_id)

    # 创建支付参数
    jpps = JsapiPayParamsService(tran.tran_id, subject, tran.pay_amount*100, nonce_str, request.remote_addr)
    if not jpps.check():
        return resjson.print_json(12, jpps.msg)

    # 创建支付参数
    jpps.create()

    return resjson.print_json(0, u'ok', {'info':jpps.pay_params})


@pay.route('/weixinjspay-notify')
def weixinjspay_notify():
    """微信jsapi支付回调"""
    resjson.action_code = 13

    xml = request.data
    jns = JsapiNotifyService(xml)
    if not jns.check():
        return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[CheckError]]></return_msg></xml>"

    if not jns.verify():
        return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[VerifyError]]></return_msg></xml>"

    pay_tran_id  = jns.transaction_id
    paid_amount  = (jns.total_fee/100)
    tran_id      = jns.out_trade_no
    current_time = current_timestamp()

    data = {'pay_tran_id':pay_tran_id, 'pay_method':'weixin_jsapi', 'paid_time':current_time, 'paid_amount':paid_amount}
    ps   = PaidService(tran_id, **data)
    ps.paid()

    return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
