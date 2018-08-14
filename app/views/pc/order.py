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
from flask_sqlalchemy import Pagination

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

from app.services.api.order import (
    OrderStaticMethodsService,
    OrderCancelService,
    OrderDeliverService
)

from app.forms.api.comment import CommentOrderGoodsForm

from app.models.comment import Comment
from app.models.shipping import Shipping
from app.models.aftersales import Aftersales
from app.models.item import Goods
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
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    data               = OrderStaticMethodsService.orders(uid, request.args.to_dict(), True)
   
    # pc端订单列表支持，支付、详情、售后3个指令，其余指令排除，即排除[2,3,4,5,6]
    if data.get("orders"):
        excel_code = [2,3,4,5,6]
        action_code = data.get('codes')
        for order in data.get("orders"):
            temp = set(action_code[order.order_id])-set(excel_code)
            action_code[order.order_id] = list(temp)

    data['tab_status'] = request.args.get('tab_status', '0')

    return render_template('pc/order/index.html.j2', **data)


@order.route('/<int:order_id>')
def detail(order_id):
    """订单详情"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    data = OrderStaticMethodsService.detail_page(order_id, uid)
    #pc端订单详情不支持再次购买，排除掉指令[5]
    data['code']= list(set(data['code'])-set([5]))
    
    return render_template('pc/order/detail.html.j2', **data)


@order.route('/cancel')
def cancel():
    """取消订单"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
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
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
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


@order.route('/create-comment/<int:og_id>')
def create_comment(og_id):
    """pc站 - 发表评价"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
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
def comment(is_pagination=True):
    """pc站 - 评价中心"""

    p          = toint(request.args.get('p', '1'))
    ps         = toint(request.args.get('ps', '10'))
    is_pending = toint(request.args.get('is_pending', '0'))


    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    completed = db.session.query(Order.order_id).\
                    filter(Order.uid == uid).\
                    filter(Order.is_remove == 0).\
                    filter(Order.order_status == 2).\
                    filter(Order.pay_status == 2).\
                    filter(Order.deliver_status == 2).all()
    completed = [order.order_id for order in completed]

    q = db.session.query(OrderGoods.og_id, OrderGoods.goods_id, OrderGoods.goods_name, OrderGoods.goods_img,
                        OrderGoods.goods_desc, OrderGoods.goods_price, OrderGoods.comment_id).\
            filter(OrderGoods.order_id.in_(completed))
    
    pending_count   = get_count(q.filter(OrderGoods.comment_id == 0))
    unpending_count = get_count(q.filter(OrderGoods.comment_id > 0))
    
    if is_pending == 1:
        q = q.filter(OrderGoods.comment_id == 0)
    else:
        q = q.filter(OrderGoods.comment_id > 0)
    
    comments = q.order_by(OrderGoods.og_id.desc()).offset((p-1)*ps).limit(ps).all()

    pagination = None
    if is_pagination:
        pagination = Pagination(None, p, ps, q.count(), None)

    data = {'is_pending':is_pending, 'pending_count':pending_count, 'unpending_count':unpending_count, 'comments':comments,'pagination':pagination}
    log_info(comments)
    return render_template('pc/order/comment.html.j2', **data)


@order.route('/comment/<int:og_id>')
def comment_detail(og_id):
    """pc站 - 查看评价"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    order_goods = OrderGoods.query.get(og_id)
    good        = Goods.query.get(order_goods.goods_id)
    comment     = Comment.query.filter(Comment.comment_id == order_goods.comment_id).filter(Comment.uid == uid).first()
    
    if not comment:
        return redirect(request.headers['Referer'])

    return render_template('pc/order/comment_detail.html.j2', order_goods=order_goods, comment=comment, good=good)
