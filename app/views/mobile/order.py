# -*- coding:utf-8 -*-
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
    url_for,
    abort
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    render_template,
    log_info,
    log_error,
    toint,
    get_count
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
from app.exception import (
    OrderException,
    ShippingException
)
from app.forms.api.comment import CommentOrderGoodsForm
from app.services.track import TrackServiceFactory
from app.services.api.order import OrderStaticMethodsService

from app.models.item import Goods
from app.models.comment import Comment
from app.models.shipping import Shipping
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods
)


order = Blueprint('mobile.order', __name__)


@order.route('/')
def index():
    """订单列表页"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data = OrderStaticMethodsService.orders(uid, request.args.to_dict())
    data['paging_url'] = url_for('mobile.order.paging', **request.args)
    data['tab_status'] = request.args.get('tab_status', '0')

    return render_template('mobile/order/index.html.j2', **data)


@order.route('/paging')
def paging():
    """加载分页"""

    if not check_login():
        session['weixin_login_url'] = url_for('mobile.order.index')
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data = OrderStaticMethodsService.orders(uid, request.args.to_dict())

    return render_template('mobile/order/paging.html.j2', **data)


@order.route('/<int:order_id>')
def detail(order_id):
    """订单详情"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data = OrderStaticMethodsService.detail_page(order_id, uid)

    return render_template('mobile/order/detail.html.j2', **data)


@order.route('/cancel')
def cancel():
    """取消订单"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))
    cancel_desc = args.get('cancel_desc', '').strip()

    if order_id <= 0:
        return ''

    ocs = OrderCancelService(order_id, uid, cancel_desc)
    try:
        ocs.cancel()
    except OrderException as e:
        msg = u'%s' % e.msg
        log_error(msg)
        return ''

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(
        ocs.order)

    return render_template(
        'mobile/order/order.html.j2',
        order=ocs.order,
        text=text,
        code=code)


@order.route('/deliver')
def deliver():
    """确认收货"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))

    if order_id <= 0:
        return ''

    ods = OrderDeliverService(order_id, uid)
    try:
        ods.deliver()
    except OrderException as e:
        msg = u'%s' % e.msg
        log_error(msg)
        return ''

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(
        ods.order)

    return render_template(
        'mobile/order/order.html.j2',
        order=ods.order,
        text=text,
        code=code)


@order.route('/track')
def track():
    """查询物流"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    args = request.args
    order_id = toint(args.get('order_id', 0))

    order = Order.query.\
        filter(Order.order_id == order_id).\
        filter(Order.uid == uid).first()

    order_address = OrderAddress.query.\
        filter(OrderAddress.order_id == order_id).first()

    shipping = None
    express_msg = ''
    express_data = []
    if order and order.shipping_status == 2:
        try:
            trackservice = TrackServiceFactory.get_trackservice()
            _express_data = trackservice.track(
                order.shipping_id,
                order.shipping_sn,
                order_address.mobile)
            express_data = _express_data
            shipping = trackservice.shipping
            express_msg = 'ok'
        except ShippingException as e:
            express_msg = e.msg

    data = {'express_msg': express_msg, 'express_data': express_data,
            'order': order, 'shipping': shipping}
    return render_template('mobile/order/track.html.j2', **data)


@order.route('/create-comment/<int:og_id>')
def create_comment(og_id):
    """手机站 - 发表评价"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_goods = OrderGoods.query.get(og_id)
    order = Order.query.filter(Order.order_id == order_goods.order_id).filter(
        Order.uid == uid).first()
    if not order:
        return redirect(url_for('mobile.index.pagenotfound'))

    if order_goods.comment_id > 0:
        return redirect(url_for('mobile.index.servererror'))

    wtf_form = CommentOrderGoodsForm()

    return render_template('mobile/order/create_comment.html.j2', order_goods=order_goods, wtf_form=wtf_form)


@order.route('/comment')
def comment():
    """手机站 - 评价中心"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data_temp = OrderStaticMethodsService.order_comments(
        uid, request.args.to_dict(), False)

    data = {'is_pending': data_temp['is_pending'], 'pending_count': data_temp['pending_count'],
            'unpending_count': data_temp['unpending_count'], 'comments': data_temp['comments']}

    return render_template('mobile/order/comment.html.j2', **data)


@order.route('/comment/<int:og_id>')
def comment_detail(og_id):
    """手机站 - 查看评价"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_goods = OrderGoods.query.get(og_id)
    good = Goods.query.get(order_goods.goods_id)
    comment = Comment.query.filter(
        Comment.comment_id == order_goods.comment_id).filter(Comment.uid == uid).first()
    if not comment:
        return redirect(url_for('mobile.index.pagenotfound'))

    return render_template('mobile/order/comment_detail.html.j2', order_goods=order_goods, comment=comment, good=good)


@order.route('/address-change/<int:oa_id>')
def address_change(oa_id):
    """手机站 - 未付款修改地址"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_address = OrderAddress.query.get(oa_id)
    if not order_address:
        return redirect(url_for('mobile.index.pagenotfound'))

    order = Order.query.\
        filter(Order.order_id == order_address.order_id).\
        filter(Order.uid == uid).first()
    if not order:
        return redirect(url_for('mobile.index.pagenotfound'))

    if order.pay_status != 1:
        return redirect(url_for('mobile.index.servererror'))

    return render_template('mobile/order/address-change.html.j2', order_address=order_address)
