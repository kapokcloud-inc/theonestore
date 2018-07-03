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
    toint,
    kt_to_dict
)
from app.helpers.date_time import (
    current_timestamp,
    date_range
)
from app.services.admin.order import OrderStaticMethodsService
from app.services.response import ResponseJson
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderTran
)


order = Blueprint('admin.order', __name__)

resjson = ResponseJson()
resjson.module_code = 11

@order.route('/index')
@order.route('/index/<int:page>')
@order.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """订单列表"""
    g.page_title = _(u'订单')

    args                    = request.args
    tab_status              = toint(args.get('tab_status', '0'))
    order_sn                = args.get('order_sn', '').strip()
    shipping_sn             = args.get('shipping_sn', '').strip()
    mobile                  = args.get('mobile', '').strip()
    name                    = args.get('name', '').strip()
    add_time_daterange      = args.get('add_time_daterange', '').strip()
    paid_time_daterange     = args.get('paid_time_daterange', '').strip()
    shipping_time_daterange = args.get('shipping_time_daterange', '').strip()

    q = db.session.query(Order.order_id, Order.order_sn, Order.goods_data, Order.goods_quantity,
                        Order.paid_time, Order.shipping_sn, Order.shipping_time, Order.order_status, Order.add_time,
                        OrderAddress.name, OrderAddress.mobile).\
            filter(Order.order_id == OrderAddress.order_id)

    if tab_status == 1:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 1)
    elif tab_status == 2:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).filter(Order.shipping_status == 1)
    elif tab_status == 3:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).filter(Order.shipping_status == 2)

    if order_sn:
        q = q.filter(Order.order_sn == order_sn)

    if shipping_sn:
        q = q.filter(Order.shipping_sn == shipping_sn)

    mobile_orders_id = None
    if mobile:
        mobile_orders_id = db.session.query(OrderAddress.order_id).filter(OrderAddress.mobile == mobile).all()
        mobile_orders_id = [_order.order_id for _order in mobile_orders_id]

    name_orders_id = None
    if name:
        name_orders_id = db.session.query(OrderAddress.order_id).filter(OrderAddress.mobile == name).all()
        name_orders_id = [_order.order_id for _order in name_orders_id]

    orders_id = None
    if mobile_orders_id is not None and name_orders_id is not None:
        orders_id = list(set(mobile_orders_id).intersection(set(name_orders_id)))
    elif mobile_orders_id is not None and name_orders_id is None:
        orders_id = mobile_orders_id
    elif mobile_orders_id is None and name_orders_id is not None:
        orders_id = name_orders_id
    if orders_id is not None:
        orders_id = [-1] if len(orders_id) == 0 else orders_id
        q = q.filter(Order.order_id.in_(orders_id))

    if add_time_daterange:
        start, end = date_range(add_time_daterange)
        q          = q.filter(Order.add_time >= start).filter(Order.add_time < end)

    if paid_time_daterange:
        start, end = date_range(paid_time_daterange)
        q          = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    if shipping_time_daterange:
        start, end = date_range(shipping_time_daterange)
        q          = q.filter(Order.shipping_time >= start).filter(Order.shipping_time < end)

    _orders    = q.order_by(Order.order_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    orders = []
    for _order in _orders:
        status_text, action_code = OrderStaticMethodsService.order_status_text_and_action_code(_order)
        _order                   = kt_to_dict(_order)
        _order['status_text']    = status_text
        orders.append(_order)

    return render_template('admin/order/index.html.j2', pagination=pagination, orders=orders)


@order.route('/detail/<int:order_id>')
def detail(order_id):
    """订单详情"""
    g.page_title = _(u'订单详情')

    order                    = Order.query.get_or_404(order_id)
    order_goods              = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
    order_address            = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()
    status_text, action_code = OrderStaticMethodsService.order_status_text_and_action_code(order)

    express_msg  = ''
    express_data = []
    if order.shipping_status == 2:
        express_msg, express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)

    return render_template('admin/order/detail.html.j2',
        order=order,
        order_goods=order_goods,
        order_address=order_address,
        status_text=status_text,
        action_code=action_code,
        express_msg=express_msg,
        express_data=express_data)


@order.route('/shipping', methods=['POST'])
def shipping():
    """确认发货"""
    resjson.action_code = 10

    form               = request.form
    order_id           = toint(form.get('order_id', 0))
    shipping_sn        = form.get('shipping_sn', '').strip()
    operation_note     = form.get('operation_note', '').strip()
    _current_timestamp = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.shipping_status == 2:
        return resjson.print_json(11, _(u'请勿重复发货'))

    if order.pay_status != 2:
        return resjson.print_json(12, _(u'未付款订单'))

    order.shipping_sn     = shipping_sn
    order.shipping_status = 2
    order.shipping_time   = _current_timestamp
    order.deliver_status  = 1
    order.update_time     = _current_timestamp

    db.session.commit()

    return resjson.print_json(0, u'ok')


@order.route('/cancel', methods=['POST'])
def cancel():
    """取消订单"""
    resjson.action_code = 11

    form               = request.form
    order_id           = toint(form.get('order_id', 0))
    cancel_desc        = form.get('cancel_desc', '').strip()
    operation_note     = form.get('operation_note', '').strip()
    _current_timestamp = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.pay_status == 2:
        return resjson.print_json(11, _(u'不能取消已付款的订单'))

    order.order_status    = 3
    order.cancel_status   = 2
    order.cancel_desc     = cancel_desc
    order.cancel_time     = _current_timestamp
    order.update_time     = _current_timestamp

    db.session.commit()

    return resjson.print_json(0, u'ok')
