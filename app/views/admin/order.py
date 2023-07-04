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
    date_range,
    timestamp2str
)
from app.exception import ShippingException

from app.services.response import ResponseJson
from app.services.message import MessageCreateService
from app.services.weixin import WeixinMessageStaticMethodsService
from app.services.admin.order import OrderStaticMethodsService
from app.services.track import TrackServiceFactory
from app.services.admin.export import ExportService

from app.models.shipping import Shipping
from app.models.user import User
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods,
    OrderTran
)


order = Blueprint('admin_order', __name__)

resjson = ResponseJson()
resjson.module_code = 14


@order.route('/index')
@order.route('/index/<int:page>')
@order.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """订单列表"""
    g.page_title = _(u'订单')

    args = request.args
    # 标签选项 0:全部订单 1:待付款 2:待发货 3:已发货
    tab_status = toint(args.get('tab_status', '0'))
    order_sn = args.get('order_sn', '').strip()
    shipping_sn = args.get('shipping_sn', '').strip()
    mobile = args.get('mobile', '').strip()
    name = args.get('name', '').strip()
    add_time_daterange = args.get('add_time_daterange', '').strip()
    paid_time_daterange = args.get('paid_time_daterange', '').strip()
    shipping_time_daterange = args.get('shipping_time_daterange', '').strip()
    submit = args.get('submit', 'search')

    # 是否导出 0:否 1:是
    is_export = 1 if submit == u'export' else 0

    export_filename = _(u'全部订单')
    q = db.session.query(Order.order_id, Order.order_sn, Order.order_status, Order.pay_status,
                         Order.paid_time, Order.shipping_sn, Order.shipping_status,
                         Order.shipping_time, Order.deliver_status, Order.goods_quantity,
                         Order.goods_data, Order.add_time, OrderAddress.name, OrderAddress.mobile,
                         Order.aftersale_status)
    if is_export == 1:
        q = db.session.query(
            # 基本信息
            Order.order_id, Order.order_sn, Order.add_time, Order.paid_time,
            Order.order_status, Order.pay_status, Order.shipping_status,
            Order.deliver_status, Order.aftersale_status,
            Order.goods_quantity, Order.goods_data, Order.goods_amount,
            Order.shipping_amount, Order.discount_amount, Order.pay_amount, Order.paid_amount,

            # 快递信息
            Order.shipping_name, Order.shipping_code, Order.shipping_sn, Order.shipping_time,

            # 收件信息
            OrderAddress.name, OrderAddress.mobile, OrderAddress.province,
            OrderAddress.city, OrderAddress.district, OrderAddress.address
        )

    q = q.filter(Order.order_id == OrderAddress.order_id).\
        filter(Order.order_type == 1)

    if tab_status == 1:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 1)
        export_filename = _(u'待付款')
    elif tab_status == 2:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).\
            filter(Order.shipping_status == 1)
        export_filename = _(u'待发货')
    elif tab_status == 3:
        q = q.filter(Order.order_status == 1).filter(Order.pay_status == 2).\
            filter(Order.shipping_status == 2)
        export_filename = _(u'已发货')

    # 订单编号
    if order_sn:
        q = q.filter(Order.order_sn == order_sn)
        export_filename += _(u' - 订单编号：') + order_sn

    # 快递号
    if shipping_sn:
        q = q.filter(Order.shipping_sn == shipping_sn)
        export_filename += _(u' - 快递号：') + shipping_sn

    # 收件人手机号
    if mobile:
        q = q.filter(OrderAddress.mobile == mobile)
        export_filename += _(u' - 手机号：') + mobile

    # 收件人姓名
    if name:
        q = q.filter(OrderAddress.name == name)
        export_filename += _(u' - 收件人姓名：') + name

    # 下单日期
    if add_time_daterange:
        start, end = date_range(add_time_daterange)
        q = q.filter(Order.add_time >= start).filter(Order.add_time < end)
        export_filename += _(u' - 下单日期：') + add_time_daterange

    # 付款日期
    if paid_time_daterange:
        start, end = date_range(paid_time_daterange)
        q = q.filter(Order.paid_time >= start).filter(Order.paid_time < end)
        export_filename += _(u' - 付款日期：') + paid_time_daterange

    # 发货日期
    if shipping_time_daterange:
        start, end = date_range(shipping_time_daterange)
        q = q.filter(Order.shipping_time >= start).filter(
            Order.shipping_time < end)
        export_filename += _(u' - 发货日期：') + shipping_time_daterange

    # 导出
    if is_export == 1:
        now = timestamp2str(current_timestamp())
        export_filename += _(u' - 导出时间：') + now
        order_list = q.order_by(Order.order_id.desc()).all()
        field_list = [
            # 订单基本信息
            {'title': _(u'订单ID'), 'field': 'order_id'},
            {'title': _(u'订单编号'), 'field': 'order_sn'},
            {'title': _(u'下单时间'), 'field': 'add_time', 'func': timestamp2str},
            {'title': _(u'订单状态'),
             'func': OrderStaticMethodsService.order_status_text},
            {'title': _(u'付款时间'), 'field': 'paid_time', 'func': timestamp2str},
            {'title': _(u'商品'), 'field': 'goods_data',
             'func': OrderStaticMethodsService.goods_list_text},
            {'title': _(u'商品数量'), 'field': 'goods_quantity'},
            {'title': _(u'商品金额'), 'field': 'goods_amount'},
            {'title': _(u'快递费用'), 'field': 'shipping_amount'},
            {'title': _(u'优惠金额'), 'field': 'discount_amount'},
            {'title': _(u'应付款'), 'field': 'pay_amount'},
            {'title': _(u'实付款'), 'field': 'paid_amount'},

            # 收件信息
            {'title': _(u'收件人'), 'field': 'name'},
            {'title': _(u'手机'), 'field': 'mobile'},
            {'title': _(u'地址'),
             'func': OrderStaticMethodsService.order_address_text},

            # 快递信息
            {'title': _(u'快递名称'), 'field': 'shipping_name'},
            {'title': _(u'快递编码'), 'field': 'shipping_code'},
            {'title': _(u'快递单号'), 'field': 'shipping_sn'},
            {'title': _(u'发货时间'), 'field': 'shipping_time',
             'func': timestamp2str},

        ]
        es = ExportService(order_list, field_list, export_filename)
        return es.export()

    orders = q.order_by(Order.order_id.desc()).offset(
        (page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)
    return render_template('admin/order/index.html.j2', pagination=pagination, orders=orders)


@order.route('/detail/<int:order_id>')
def detail(order_id):
    """订单详情"""
    g.page_title = _(u'订单详情')

    order = Order.query.get_or_404(order_id)
    user = User.query.get(order.uid)
    order_goods = OrderGoods.query.\
        filter(OrderGoods.order_id == order_id).all()
    order_address = OrderAddress.query.\
        filter(OrderAddress.order_id == order_id).first()
    status_text, action_code = OrderStaticMethodsService.\
        order_status_text_and_action_code(order)

    express_msg = _(u'暂无物流信息')
    express_data = []
    if order.shipping_status == 2:
        try:
            ts = TrackServiceFactory.get_trackservice()
            express_datas = ts.track(
                order.shipping_id,
                order.shipping_sn,
                order_address.mobile)
            express_data = express_datas
            express_msg = 'ok'
        except ShippingException as e:
            express_msg = e.msg

    shipping_list = Shipping.query.\
        filter(Shipping.is_enable == 1).\
        order_by(Shipping.sorting.desc()).all()

    data = {
        'order': order,
        'user': user,
        'order_address': order_address,
        'order_goods': order_goods,
        'status_text': status_text,
        'action_code': action_code,
        'express_msg': express_msg,
        'express_data': express_data,
        'shipping_list': shipping_list}
    return render_template('admin/order/detail.html.j2', **data)


@order.route('/shipping', methods=['POST'])
def shipping():
    """确认发货"""
    resjson.action_code = 10

    form = request.form
    order_id = toint(form.get('order_id', 0))
    shipping_sn = form.get('shipping_sn', '').strip()
    # operation_note = form.get('operation_note', '').strip()
    shipping_id = toint(form.get('shipping_id', 0))
    current_time = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))

    if order.shipping_status == 2:
        return resjson.print_json(11, _(u'请勿重复发货'))

    if order.pay_status != 2:
        return resjson.print_json(12, _(u'未付款订单'))

    if shipping_sn == '':
        return resjson.print_json(13, _(u'请填写快递单号'))
    
    shipping = Shipping.query.get(shipping_id)
    if not shipping:
        return resjson.print_json(14, _(u'物流公司不存在'))
    
    order.shipping_id = shipping.shipping_id
    order.shipping_name = shipping.shipping_name
    order.shipping_code = shipping.shipping_code
    order.shipping_sn = shipping_sn
    order.shipping_status = 2
    order.shipping_time = current_time
    order.deliver_status = 1
    order.update_time = current_time

    # 站内消息
    content = _(u'您的订单%s已发货，%s，快递单号%s，请注意查收。' %
                (order.order_sn, order.shipping_name, shipping_sn))
    mcs = MessageCreateService(
        1,
        order.uid,
        -1,
        content,
        ttype=1,
        tid=order_id,
        current_time=current_time)
    if not mcs.check():
        log_error('[ErrorViewAdminOrderShipping][MessageCreateError]  order_id:%s msg:%s' % (
            order_id, mcs.msg))
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

    form = request.form
    order_id = toint(form.get('order_id', 0))
    cancel_desc = form.get('cancel_desc', '').strip()
    # operation_note = form.get('operation_note', '').strip()
    current_time = current_timestamp()

    order = Order.query.get(order_id)
    if not order:
        return resjson.print_json(10, _(u'订单不存在'))
    
    if order.pay_status == 2:
        return resjson.print_json(11, _(u'不能取消已付款的订单'))

    if order.shipping_status == 2:
        return resjson.print_json(13, _(u'订单已经发货，不能取消'))
    
    if order.order_status == 2:
        return resjson.print_json(14, _(u'订单已经完成，不能取消'))

    order.order_status = 3
    order.cancel_status = 2
    order.cancel_desc = cancel_desc
    order.cancel_time = current_time
    order.update_time = current_time

    db.session.commit()
    return resjson.print_json(0, u'ok')
