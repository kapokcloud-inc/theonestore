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

from app.database import db

from app.helpers import (
    render_template,
    log_info,
    toint,
    get_count
)
from app.helpers.user import (
    check_login,
    get_uid
)
from app.helpers.date_time import current_timestamp

from app.services.api.order import (
    OrderStaticMethodsService,
    OrderCancelService,
    OrderDeliverService
)

from app.forms.api.comment import CommentOrderGoodsForm

from app.models.comment import Comment
from app.models.shipping import Shipping
from app.models.order import (
    Order,
    OrderAddress,
    OrderGoods
)


order = Blueprint('pc.order', __name__)

@order.route('/')
def index():
    """订单列表页"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    orders     = OrderStaticMethodsService.orders(uid, request.args.to_dict())
    paging_url = url_for('pc.order.paging', **request.args)

    texts = {}
    codes = {}
    for order in orders:
        text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)
        texts[order.order_id] = text
        codes[order.order_id] = code
    
    tab_status = toint(request.args.get('tab_status', '0'))

    data = {'tab_status':tab_status, 'orders':orders, 'texts':texts, 'codes':codes, 'paging_url':paging_url}
    return render_template('pc/order/index.html.j2', **data)


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

    return render_template('pc/order/paging.html.j2', orders=orders, texts=texts, codes=codes)


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

    items         = OrderGoods.query.filter(OrderGoods.order_id == order_id).all()
    order_address = OrderAddress.query.filter(OrderAddress.order_id == order_id).first()

    text, code = OrderStaticMethodsService.order_status_text_and_action_code(order)

    express_data = None
    if order.shipping_status == 2:
        _express_msg, _express_data = OrderStaticMethodsService.track(order.shipping_code, order.shipping_sn)
        if _express_msg == 'ok':
            express_data = _express_data[0] if len(_express_data) > 0 else {}

    data = {'order':order, 'items':items, 'order_address':order_address, 'text':text, 'code':code, 'express_data':express_data,
            'current_time':current_timestamp()}
    return render_template('pc/order/detail.html.j2', **data)


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

    return render_template('pc/order/order.html.j2', order=ocs.order, text=text, code=code)


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

    return render_template('pc/order/order.html.j2', order=ods.order, text=text, code=code)


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
    return render_template('pc/order/track.html.j2', **data)


@order.route('/create-comment/<int:og_id>')
def create_comment(og_id):
    """手机站 - 发表评价"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_goods = OrderGoods.query.get(og_id)
    order       = Order.query.filter(Order.order_id == order_goods.order_id).filter(Order.uid == uid).first()
    if not order:
        return redirect(request.headers['Referer'])
    
    if order_goods.comment_id > 0:
        return redirect(request.headers['Referer'])
    
    wtf_form = CommentOrderGoodsForm()

    return render_template('pc/order/create_comment.html.j2', order_goods=order_goods, wtf_form=wtf_form)


@order.route('/comment')
def comment():
    """手机站 - 评价中心"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    is_pending = toint(request.args.get('is_pending', '0'))

    completed = db.session.query(Order.order_id).\
                    filter(Order.uid == uid).\
                    filter(Order.is_remove == 0).\
                    filter(Order.order_status == 2).\
                    filter(Order.pay_status == 2).\
                    filter(Order.deliver_status == 2).all()
    completed = [order.order_id for order in completed]

    q = db.session.query(OrderGoods.og_id, OrderGoods.goods_id, OrderGoods.goods_name, OrderGoods.goods_img,
                        OrderGoods.goods_desc, OrderGoods.comment_id).\
            filter(OrderGoods.order_id.in_(completed))
    
    pending_count   = get_count(q.filter(OrderGoods.comment_id == 0))
    unpending_count = get_count(q.filter(OrderGoods.comment_id > 0))
    
    if is_pending == 1:
        q = q.filter(OrderGoods.comment_id == 0)
    else:
        q = q.filter(OrderGoods.comment_id > 0)
    
    uncomments = q.order_by(OrderGoods.og_id.desc()).all()

    data = {'is_pending':is_pending, 'pending_count':pending_count, 'unpending_count':unpending_count, 'uncomments':uncomments}
    return render_template('pc/order/comment.html.j2', **data)


@order.route('/comment/<int:og_id>')
def comment_detail(og_id):
    """手机站 - 查看评价"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_goods = OrderGoods.query.get(og_id)
    comment     = Comment.query.filter(Comment.comment_id == order_goods.comment_id).filter(Comment.uid == uid).first()
    if not comment:
        return redirect(request.headers['Referer'])

    return render_template('pc/order/comment_detail.html.j2', order_goods=order_goods, comment=comment)

