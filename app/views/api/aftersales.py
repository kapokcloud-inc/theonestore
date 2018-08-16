# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import (
    Blueprint,
    request,
    session
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
from app.services.api.aftersales import AfterSalesCreateService, AfterSalesStaticMethodsService

from app.forms.api.aftersales import AfterSalesForm

from app.models.order import Order, OrderGoods


aftersales = Blueprint('api.aftersales', __name__)

resjson = ResponseJson()
resjson.module_code = 16

@aftersales.route('/apply', methods=['POST'])
def apply():
    """申请售后"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    wtf_form = AfterSalesForm()
    if not wtf_form.validate_on_submit():
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    og_id           = toint(request.form.get('og_id', '0'))
    order_id        = toint(request.form.get('order_id', '0'))
    quantity        = toint(request.form.get('quantity', '0'))
    aftersales_type = toint(request.form.get('aftersales_type', '0'))
    deliver_status  = toint(request.form.get('deliver_status', '0'))
    content         = request.form.get('content', '').strip()
    img_data        = request.form.get('img_data', '[]').strip()

    data = {'uid':uid, 'order_id':order_id, 'og_id':og_id, 'quantity':quantity,
            'aftersales_type':aftersales_type, 'deliver_status':deliver_status,
            'content':content, 'img_data':img_data}
    ascs = AfterSalesCreateService(**data)
    if not ascs.check():
        return resjson.print_json(12, ascs.msg)

    ascs.create()

    return resjson.print_json(0, u'ok')


@aftersales.route('/refunds-amount')
def refunds_amount():
    """获取退款金额"""
    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    og_id    = toint(request.args.get('og_id', '0'))
    quantity = toint(request.args.get('quantity', '0'))
    if og_id <= 0 or quantity <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    order_goods = OrderGoods.query.get(og_id)
    if not order_goods:
        return resjson.print_json(resjson.PARAM_ERROR)
    
    order = Order.query.filter(Order.order_id == order_goods.order_id).filter(Order.uid == uid).first()
    if not order:
        return resjson.print_json(resjson.PARAM_ERROR)

    refunds_amount = AfterSalesStaticMethodsService.refunds_amount(order_goods=order_goods, quantity=quantity)

    return resjson.print_json(0, u'ok', {'refunds_amount':refunds_amount})
