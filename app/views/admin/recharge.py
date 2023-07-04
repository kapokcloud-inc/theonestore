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
from werkzeug.datastructures import CombinedMultiDict

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    log_error,
    toint,
    kt_to_dict,
    get_count
)


from app.helpers.date_time import (
    current_timestamp,
    date_range,
    some_day_timestamp,
)

from app.models.user import User
from app.models.order import (
    Order,
    OrderTran
)

from app.services.response import ResponseJson


recharge = Blueprint('admin_recharge', __name__)

resjson = ResponseJson()
resjson.module_code = 21


@recharge.route('/index')
@recharge.route('/index/<int:page>')
@recharge.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """订单列表"""
    g.page_title = _(u'充值')
    
    # 金额筛选项
    amounts = [
            {'name': _(u'请选择...'), 'value': '-1'},
            {'name': _(u'50元以下'), 'value': '0'},
            {'name': _(u'100元以下'), 'value': '1'},
            {'name': _(u'100元以上'), 'value': '2'}
        ]

    args                = request.args
    tab_status          = toint(args.get('tab_status', '0'))
    order_sn            = args.get('order_sn', '').strip()
    pay_tran_id         = args.get('pay_tran_id', '').strip()
    uid                 = toint(args.get('uid', '0').strip())
    order_amount        = toint(args.get('order_amount', '-1').strip())
    paid_time_daterange = args.get('paid_time_daterange', '').strip()

    q = db.session.query(Order.order_id, Order.order_sn, Order.order_status, Order.order_amount,
                            Order.pay_status, Order.paid_time, Order.pay_tran_id, Order.add_time, 
                            User.nickname, User.avatar).\
                            filter(Order.uid == User.uid).\
                            filter(Order.pay_status == 2).\
                            filter(Order.order_type == 2)

    # 今天
    if tab_status == 1:
        start = some_day_timestamp(current_timestamp(), 0)
        end   = some_day_timestamp(current_timestamp(), 1)
        q     = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    # 昨天
    elif tab_status == 2:
        start = some_day_timestamp(current_timestamp(), -1)
        end   = some_day_timestamp(current_timestamp(), 0)
        q     = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    # 一周内
    elif tab_status == 3:
        start = some_day_timestamp(current_timestamp(), -7)
        end   = some_day_timestamp(current_timestamp(), 0)
        q     = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    # 自定义时间段
    elif tab_status == 0 and paid_time_daterange:
        start, end = date_range(paid_time_daterange)
        q          = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    if order_sn:
        q = q.filter(Order.order_sn == order_sn)
    
    if pay_tran_id:
        q = q.filter(Order.pay_tran_id == pay_tran_id)
    
    if uid:
        q = q.filter(Order.uid == uid)
    
    if order_amount == 0:
        q = q.filter(Order.order_amount < 50)
    elif order_amount == 1:
        q = q.filter(Order.order_amount < 100)
    elif  order_amount == 2:
        q = q.filter(Order.order_amount >= 100)
        
    orders = q.order_by(Order.order_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/recharge/index.html.j2', pagination=pagination, orders=orders , amounts=amounts)
