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
    toint,
    kt_to_dict
)
from app.helpers.date_time import (
    current_timestamp,
    date_range
)

from app.services.response import ResponseJson
from app.services.message import MessageCreateService
from app.services.weixin import WeixinMessageStaticMethodsService
from app.services.admin.order import OrderStaticMethodsService

from app.models.user import User
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderTran
)


order = Blueprint('admin.order', __name__)

resjson = ResponseJson()
resjson.module_code = 14

@order.route('/index')
@order.route('/index/<int:page>')
@order.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """订单列表"""
    g.page_title = _(u'订单')

    args                    = request.args
    # 标签选项 0:全部订单 1:待付款 2:待发货 3:已发货
    tab_status              = toint(args.get('tab_status', '0'))
    order_sn                = args.get('order_sn', '').strip()
    shipping_sn             = args.get('shipping_sn', '').strip()
    mobile                  = args.get('mobile', '').strip()
    name                    = args.get('name', '').strip()
    add_time_daterange      = args.get('add_time_daterange', '').strip()
    paid_time_daterange     = args.get('paid_time_daterange', '').strip()
    shipping_time_daterange = args.get('shipping_time_daterange', '').strip()

    q = db.session.query(Order.order_id, Order.order_sn, Order.order_status, Order.pay_status,
                        Order.paid_time, Order.shipping_sn, Order.shipping_status,
                        Order.shipping_time, Order.deliver_status, Order.goods_quantity,
                        Order.goods_data, Order.add_time, OrderAddress.name, OrderAddress.mobile,
                        Order.aftersale_status).\
            filter(Order.order_id == OrderAddress.order_id).\
            filter(Order.order_type == 1)

    if tab_status == 1:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 1)
    elif tab_status == 2:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).filter(Order.shipping_status == 1)
    elif tab_status == 3:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).filter(Order.shipping_status == 2)

    # 订单编号
    if order_sn:
        q = q.filter(Order.order_sn == order_sn)

    # 快递号
    if shipping_sn:
        q = q.filter(Order.shipping_sn == shipping_sn)

    # 收件人手机号
    if mobile:
        q = q.filter(OrderAddress.mobile == mobile)

    # 收件人姓名
    if name:
        q = q.filter(OrderAddress.name == name)

    # 下单日期
    if add_time_daterange:
        start, end = date_range(add_time_daterange)
        q = q.filter(Order.add_time >= start).filter(Order.add_time < end)

    # 付款日期
    if paid_time_daterange:
        start, end = date_range(paid_time_daterange)
        q = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)

    # 发货日期
    if shipping_time_daterange:
        start, end = date_range(shipping_time_daterange)
        q = q.filter(Order.shipping_time >= start).filter(Order.shipping_time < end)

    orders = q.order_by(Order.order_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)
    return render_template('admin/order/index.html.j2', pagination=pagination, orders=orders)


@order.route('/detail/<int:order_id>')
def detail(order_id):
    """订单详情"""
    g.page_title = _(u'订单详情')

    order                    = Order.query.get_or_404(order_id)
    user                     = User.query.get(order.uid)
    order_goods              = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
    order_address            = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()
    status_text, action_code = OrderStaticMethodsService.order_status_text_and_action_code(order)

    express_msg  = ''
    express_data = []
    if order.shipping_status == 2:
        express_msg, express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)

    data = {'order':order, 'user':user, 'order_address':order_address,
            'order_goods':order_goods, 'status_text':status_text, 'action_code':action_code,
            'express_msg':express_msg, 'express_data':express_data}
    return render_template('admin/order/detail.html.j2', **data)


@order.route('/shipping', methods=['POST'])
def shipping():
    """确认发货"""
    resjson.action_code = 10

    form           = request.form
    order_id       = toint(form.get('order_id', 0))
    shipping_sn    = form.get('shipping_sn', '').strip()
    operation_note = form.get('operation_note', '').strip()
    current_time   = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.shipping_status == 2:
        return resjson.print_json(11, _(u'请勿重复发货'))

    if order.pay_status != 2:
        return resjson.print_json(12, _(u'未付款订单'))
    
    if shipping_sn == '':
        return resjson.print_json(13, _(u'请填写快递单号'))

    order.shipping_sn     = shipping_sn
    order.shipping_status = 2
    order.shipping_time   = current_time
    order.deliver_status  = 1
    order.update_time     = current_time

    # 站内消息
    content = _(u'您的订单%s已发货，%s，快递单号%s，请注意查收。' % (order.order_sn, order.shipping_name, shipping_sn))
    mcs = MessageCreateService(1, order.uid, -1, content, ttype=1, tid=order_id, current_time=current_time)
    if not mcs.check():
        log_error('[ErrorViewAdminOrderShipping][MessageCreateError]  order_id:%s msg:%s' % (order_id, mcs.msg))
    else:
        mcs.do()

    db.session.commit()

    # 微信消息
    WeixinMessageStaticMethodsService.shipping(order)

    return resjson.print_json(0, u'ok')


@order.route('/cancel', methods=['POST'])
def cancel():
    """取消订单"""
    resjson.action_code = 11

    form           = request.form
    order_id       = toint(form.get('order_id', 0))
    cancel_desc    = form.get('cancel_desc', '').strip()
    operation_note = form.get('operation_note', '').strip()
    current_time   = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.pay_status == 2:
        return resjson.print_json(11, _(u'不能取消已付款的订单'))

    order.order_status    = 3
    order.cancel_status   = 2
    order.cancel_desc     = cancel_desc
    order.cancel_time     = current_time
    order.update_time     = current_time

    db.session.commit()

    return resjson.print_json(0, u'ok')
