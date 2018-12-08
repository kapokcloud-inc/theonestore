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
    Blueprint,
    request,
    session
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint,
    model_update
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.response import ResponseJson
from app.services.api.aftersales import (
    AfterSalesCreateService, 
    AfterSalesStaticMethodsService
)

from app.forms.api.aftersales import AfterSalesForm
from app.models.order import Order, OrderGoods
from app.models.sys import SysSetting
from app.models.aftersales import (
    Aftersales,
    AftersalesAddress,
    AftersalesLogs
)


aftersales = Blueprint('api.aftersales', __name__)

resjson = ResponseJson()
resjson.module_code = 16

@aftersales.route('/apply', methods=['POST'])
def apply():
    """申请售后"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
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

    aftersales_id = ascs.create()

    return resjson.print_json(0, u'ok', {'aftersales_id':aftersales_id})


@aftersales.route('/refunds-amount')
def refunds_amount():
    """获取退款金额"""
    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
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


@aftersales.route('/return-goods', methods=['POST'])
def return_goods():
    """寄回商品"""
    resjson.action_code = 12

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    aftersales_id      = toint(request.form.get('aftersales_id', '0'))
    return_shipping_sn = request.form.get('return_shipping_sn', '').strip()
    current_time       = current_timestamp()

    if aftersales_id <= 0 or return_shipping_sn == '':
        return resjson.print_json(resjson.PARAM_ERROR)

    aftersales = Aftersales.query.\
                    filter(Aftersales.aftersales_id == aftersales_id).\
                    filter(Aftersales.uid == uid).first()
    if not aftersales:
        return resjson.print_json(10, _(u'售后不存在'))

    if aftersales.aftersales_type not in [2,3]:
        return resjson.print_json(11, _(u'售后类型错误'))

    if aftersales.return_status != 1:
        return resjson.print_json(12, _(u'寄回状态错误'))

    data = {'return_shipping_sn':return_shipping_sn, 'return_status':2}
    model_update(aftersales, data)

    content = _(u'快递单号:%s，我们收到退货/换货商品后，需要1-3个工作日处理，请耐心等待。' % return_shipping_sn)
    AfterSalesStaticMethodsService.add_log(aftersales_id, content, 6, current_time, commit=True)

    return resjson.print_json(0, u'ok')

@aftersales.route('/index')
def index():
    """ 售后服务列表 """

    resjson.action_code = 13

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))

    if p <= 0 or ps <=0:
         return resjson.print_json(resjson.PARAM_ERROR)
    
    params = {'uid':uid, 'p':p, 'ps':ps}
    _data  = AfterSalesStaticMethodsService.aftersales(params)

    aftersales_status_text = {}
    for aftersale in _data['aftersales']:
        status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersale)
        aftersales_status_text[aftersale.aftersales_id] = status_text

    data = {'aftersales':_data['aftersales'],'aftersales_status_text':aftersales_status_text}
    return resjson.print_json(0, u'ok', data)

@aftersales.route('/detail')
def detail():
    """ 售后服务详情 """

    resjson.action_code = 14

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    aftersales_id = toint(request.args.get('aftersales_id', '0'))
    if aftersales_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).filter(Aftersales.uid == uid).first()
    if not aftersales:
        return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)
    
    log = AftersalesLogs.query.\
            filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
            order_by(AftersalesLogs.al_id.desc()).first()

    status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersales)

    aftersales_service = {}
    if aftersales.check_status == 2:
        ss = SysSetting.query.filter(SysSetting.key == 'config_aftersales_service').first()
        if ss:
            try:
                aftersales_service = json.loads(ss.value)
            except Exception as e:
                aftersales_service = {}

    address = AftersalesAddress.query.filter(AftersalesAddress.aftersales_id == aftersales_id).first()

    data = {'aftersales':aftersales, 'log':log, 'status_text':status_text,
            'action_code':action_code, 'aftersales_service':aftersales_service, 'address':address}
    return resjson.print_json(0, u'ok', data)

@aftersales.route('/track')
def track():
    """ 售后服务流水跟踪 """

    resjson.action_code = 15

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    aftersales_id = toint(request.args.get('aftersales_id', '0'))
    if aftersales_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).\
                                    filter(Aftersales.uid == uid).first()
    if not aftersales:
        return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)

    logs = AftersalesLogs.query.\
                filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
                order_by(AftersalesLogs.al_id.desc()).all()

    return resjson.print_json(0, u'ok', {'logs': logs})

@aftersales.route('/apply/info')
def apply_info():
    """ 申请售后 """

    resjson.action_code = 16

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    order_id = toint(request.args.get('order_id', '0'))
    og_id    = toint(request.args.get('og_id', '0'))

    if order_id <= 0 and og_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)
    wtf_form = AfterSalesForm()
    if order_id > 0:
        ascs = AfterSalesCreateService(uid, order_id=order_id, og_id=0, quantity=1, aftersales_type=1, deliver_status=1)
        ret  = ascs._check_order()
        if not ret:
            return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)

        data = {'wtf_form': wtf_form, 'order_id':order_id, 'goods_data':ascs.goods_data, 'refunds_amount':ascs.refunds_amount}
        return resjson.print_json(0, u'ok', data)
    else:
        aftersales_type = 2
        ascs = AfterSalesCreateService(uid, order_id=0, og_id=og_id, quantity=1, aftersales_type=aftersales_type, deliver_status=1)
        ret  = ascs._check_order_goods()
        if not ret:
            if ascs.msg != u'超过有效退款时间':
                return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)

            aftersales_type = 3
            ascs = AfterSalesCreateService(uid, order_id=0, og_id=og_id, quantity=1,
                                            aftersales_type=aftersales_type, deliver_status=1)
            ret  = ascs._check_order_goods()
            if not ret:
                return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)

        data = {'wtf_form': wtf_form, 'goods_data':ascs.goods_data,'refunds_amount':ascs.refunds_amount, 'order_address':ascs.order_address, 'aftersales_type':aftersales_type}

        return resjson.print_json(0, u'ok', data)
