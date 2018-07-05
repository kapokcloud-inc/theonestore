# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _

from app.helpers import (
    render_template,
    log_info,
    toint
)
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.api.order import (
    OrderStaticMethodsService,
    OrderCancelService,
    OrderDeliverService
)

from app.models.shipping import Shipping
from app.models.order import (
    Order,
    OrderAddress
)


order = Blueprint('mobile.order', __name__)

@order.route('/')
def index():
    """订单列表页"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    orders     = OrderStaticMethodsService.orders(uid, request.args.to_dict())
    paging_url = url_for('mobile.order.paging', **request.args)

    texts = {}
    codes = {}
    for order in orders:
        text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)
        texts[order.order_id] = text
        codes[order.order_id] = code
    
    tab_status = toint(request.args.get('tab_status', '0'))

    data = {'tab_status':tab_status, 'orders':orders, 'texts':texts, 'codes':codes, 'paging_url':paging_url}
    return render_template('mobile/order/index.html.j2', **data)


@order.route('/paging')
def paging():
    """加载分页"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    orders = OrderStaticMethodsService.orders(uid, request.args.to_dict())

    texts = {}
    codes = {}
    for order in orders:
        text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)
        texts[order.order_id] = text
        codes[order.order_id] = code

    return render_template('mobile/order/paging.html.j2', orders=orders, texts=texts, codes=codes)


@order.route('/<int:order_id>')
def detail(order_id):
    """订单详情"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
    if not order:
        return redirect(request.headers['Referer'])
    
    order_address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)

    express_data = None
    if order.shipping_status == 2:
        _express_msg, _express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)
        if _express_msg == 'ok':
            express_data = _express_data[0] if len(_express_data) > 0 else {}

    data = {'order':order, 'order_address':order_address, 'text':text, 'code':code, 'express_data':express_data}
    return render_template('mobile/order/detail.html.j2', **data)


@order.route('/cancel')
def cancel():
    """取消订单"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args        = request.args
    order_id    = toint(args.get('order_id', 0))
    cancel_desc = args.get('cancel_desc', '').strip()

    if order_id <= 0:
        return ''

    ocs = OrderCancelService(order_id, uid, cancel_desc)

    if not ocs.check():
        return ''

    ocs.cancel()
    ocs.commit()

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(ocs.order)

    return render_template('mobile/order/order.html.j2', order=ocs.order, text=text, code=code)


@order.route('/deliver')
def deliver():
    """确认收货"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args     = request.args
    order_id = toint(args.get('order_id', 0))

    if order_id <= 0:
        return ''
    
    ods = OrderDeliverService(order_id, uid)
    if not ods.check():
        return ''

    ods.deliver()
    ods.commit()

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(ods.order)

    return render_template('mobile/order/order.html.j2', order=ods.order, text=text, code=code)


@order.route('/track')
def track():
    """查询物流"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args     = request.args
    order_id = toint(args.get('order_id', 0))

    order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()

    shipping     = None
    express_msg  = ''
    express_data = []
    if order and order.shipping_status == 2:
        shipping = Shipping.query.get(order.shipping_id)

        express_msg, _express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)
        if express_msg == 'ok':
            express_data = _express_data

    data = {'express_msg':express_msg, 'express_data':express_data, 'order':order, 'shipping':shipping}
    return render_template('mobile/order/track.html.j2', **data)


@order.route('/create-comment')
def create_comment():
    """手机站 - 发表评价"""
    return render_template('mobile/order/create_comment.html.j2')


@order.route('/comment')
def comment():
    """手机站 - 评价中心"""
    return render_template('mobile/order/comment.html.j2')


@order.route('/comment/<int:comment_id>')
def comment_detail(comment_id):
    """手机站 - 查看评价"""
    return render_template('mobile/order/comment_detail.html.j2')

