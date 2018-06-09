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
    toint
)
from app.helpers.date_time import (
    current_timestamp,
    date_range
)

from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderTran
)


order = Blueprint('admin.order', __name__)

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
        q = q.filter(Order.pay_status == 1)
    elif tab_status == 2:
        q = q.filter(Order.pay_status == 2).filter(Order.shipping_status == 1)
    elif tab_status == 3:
        q = q.filter(Order.shipping_status == 2)

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

    orders     = q.order_by(Order.order_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/order/index.html.j2', pagination=pagination, orders=orders)


@order.route('/detail/<int:order_id>')
def detail(order_id):
    """订单详情"""
    g.page_title = _(u'订单详情')

    order = Order.query.get_or_404(order_id)

    return render_template('admin/order/detail.html.j2', wtf_form=wtf_form, order=order)

