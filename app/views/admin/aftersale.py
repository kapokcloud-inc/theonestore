# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for,
    g
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    log_error,
    toint
)
from app.helpers.date_time import current_timestamp

from app.services.response import ResponseJson
from app.services.admin.order import OrderStaticMethodsService
from app.services.admin.aftersale import (
    AfterSaleCheckService,
    AfterSaleReceivedService,
    AfterSaleResendService,
    AfterSaleRefundsService,
    AfterSaleStaticMethodsService
)

from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods
)
from app.models.aftersales import (
    Aftersales,
    AftersalesAddress,
    AftersalesGoods,
    AftersalesLogs
)


aftersale = Blueprint('admin.aftersale', __name__)

resjson = ResponseJson()
resjson.module_code = 17

@aftersale.route('/index')
@aftersale.route('/index/<int:page>')
@aftersale.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """售后列表"""
    g.page_title = _(u'售后')

    args                    = request.args
    tab_status              = toint(args.get('tab_status', '0'))

    q = Aftersales.query

    if tab_status == 1:
        q = q.filter(Aftersales.aftersales_type == 1)
    elif tab_status == 2:
        q = q.filter(Aftersales.aftersales_type == 2)
    elif tab_status == 3:
        q = q.filter(Aftersales.aftersales_type == 3)
    elif tab_status == 4:
        q = q.filter(Aftersales.status == 2).filter(Aftersales.return_status == 2)
    elif tab_status == 5:
        q = q.filter(Aftersales.status == 2).filter(Aftersales.return_status == 3).filter(Aftersales.resend_status == 1)

    aftersalses = q.order_by(Aftersales.aftersales_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination  = Pagination(None, page, page_size, q.count(), None)

    texts = {}
    codes = {}
    for aftersalse in aftersalses:
        text, code = AfterSaleStaticMethodsService.aftersale_status_text_and_action_code(aftersalse)
        texts[aftersalse.aftersales_id] = text
        codes[aftersalse.aftersales_id] = code

    data = {'pagination':pagination, 'aftersalses':aftersalses, 'texts':texts}
    return render_template('admin/aftersale/index.html.j2', **data)


@aftersale.route('/detail/<int:aftersales_id>')
def detail(aftersales_id):
    """售后详情"""
    g.page_title = _(u'售后详情')

    aftersale                = Aftersales.query.get_or_404(aftersales_id)
    status_text, action_code = AfterSaleStaticMethodsService.aftersale_status_text_and_action_code(aftersale)
    aftersale_goods          = AftersalesGoods.query.filter(AftersalesGoods.aftersales_id == aftersales_id).all()

    order         = Order.query.get_or_404(aftersale.order_id)
    order_address = OrderAddress.query.filter(OrderAddress.order_id == aftersale.order_id).first()
    order_goods   = OrderGoods.query.filter(OrderGoods.order_id == aftersale.order_id).order_by(OrderGoods.og_id.desc()).all()
    order_status_text, order_action_code = OrderStaticMethodsService.order_status_text_and_action_code(order)

    logs    = AftersalesLogs.query.\
                    filter(AftersalesLogs.aftersales_id == aftersales_id).\
                    order_by(AftersalesLogs.al_id.desc()).all()
    address = AftersalesAddress.query.\
                    filter(AftersalesAddress.aftersales_id == aftersales_id).first()

    data = {'aftersale':aftersale, 'aftersale_goods':aftersale_goods, 'status_text':status_text, 'action_code':action_code,
            'order':order, 'order_address':order_address, 'order_goods':order_goods, 'order_status_text':order_status_text,
            'logs':logs, 'address':address}
    return render_template('admin/aftersale/detail.html.j2', **data)


@aftersale.route('/check', methods=['POST'])
def check():
    """售后审核"""
    resjson.action_code = 10

    form          = request.form
    aftersales_id = toint(form.get('aftersales_id', 0))
    check_status  = toint(form.get('check_status', 0))
    content       = form.get('content', '').strip()

    ascs = AfterSaleCheckService(aftersales_id, check_status, content)
    if not ascs.check():
        return resjson.print_json(10, ascs.msg)

    ascs.do()

    return resjson.print_json(0, u'ok')


@aftersale.route('/received')
def received():
    """已签收"""
    resjson.action_code = 11

    args          = request.args
    aftersales_id = toint(args.get('aftersales_id', 0))

    asrs = AfterSaleReceivedService(aftersales_id)
    if not asrs.check():
        return resjson.print_json(10, asrs.msg)

    asrs.do()

    return resjson.print_json(0, u'ok')


@aftersale.route('/resend', methods=['POST'])
def resend():
    """重发商品"""
    resjson.action_code = 12

    form                 = request.form
    aftersales_id        = toint(form.get('aftersales_id', 0))
    resend_shipping_name = form.get('resend_shipping_name', '').strip()
    resend_shipping_sn   = form.get('resend_shipping_sn', '').strip()

    asrs = AfterSaleResendService(aftersales_id, resend_shipping_name, resend_shipping_sn)
    if not asrs.check():
        return resjson.print_json(10, asrs.msg)

    asrs.do()

    return resjson.print_json(0, u'ok')


@aftersale.route('/refunds')
def refunds():
    """退款"""
    resjson.action_code = 13

    args          = request.args
    aftersales_id = toint(args.get('aftersales_id', 0))

    asrs = AfterSaleRefundsService(aftersales_id)
    if not asrs.check():
        return resjson.print_json(10, asrs.msg)

    if not asrs.do():
        return resjson.print_json(11, asrs.msg)

    return resjson.print_json(0, u'ok')
