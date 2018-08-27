# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal

from flask_babel import gettext as _
from flask import (
    request,
    session,
    make_response,
    Blueprint,
    g,
    redirect,
    url_for
)
from sqlalchemy import func

from app.services.admin.order import OrderStaticMethodsService

from app.models.user import User
from app.models.order import Order
from app.models.aftersales import Aftersales
from app.models.comment import Comment

from app.database import db

from app.helpers import (
    render_template,
    log_info,
    kt_to_dict
)


index = Blueprint('admin.index', __name__)

@index.route('/')
def root():
    """管理后台首页"""
    admin_uid = session.get('admin_uid', None)
    if admin_uid:
        return redirect(url_for('admin.index.dashboard'))
    return_url = request.args.get('return_url', '/admin/dashboard')
    return redirect(url_for('admin.auth.login', return_url=return_url))


@index.route('/dashboard')
def dashboard():
    """dashboard页"""
    admin_uid = session.get('admin_uid', None)
    if not admin_uid:
        return_url = request.args.get('return_url', '/admin/dashboard')
        return redirect(url_for('admin.auth.login', return_url=return_url))
    #用户数
    sum_user           = User.query.count()

    #订单数
    sum_order          = Order.query.count()

    #订单交易总额
    _sum_order_amount  = db.session.query(func.sum(Order.order_amount).label('sum_order_amount')).\
                            filter(Order.order_type == 1).\
                            filter(Order.pay_status == 2).first()
    sum_order_amount   = _sum_order_amount.sum_order_amount if _sum_order_amount else Decimal('0.00')

    #售后数
    sum_aftersales     = Aftersales.query.count()

    #会员充值(连表查，3条数据)
    funds_orders       = db.session.query(Order.order_id, Order.order_amount, Order.add_time,
                                        User.nickname, User.avatar).\
                                    filter(Order.uid == User.uid).\
                                    filter(Order.order_type == 2).\
                                    filter(Order.pay_status == 2).\
                                    order_by(Order.order_id.desc()).limit(4).all()
    fund_orders_amount = 0
    for funds_order in funds_orders:
        fund_orders_amount += funds_order.order_amount

    #最近订单
    goods_orders       = db.session.query(Order.order_id, Order.order_sn, Order.order_amount, 
                                        Order.order_status, Order.pay_status, Order.shipping_status, 
                                        Order.deliver_status, Order.aftersale_status, Order.add_time, 
                                        User.nickname, User.avatar).\
                                    filter(Order.uid == User.uid).\
                                    filter(Order.order_type == 1).\
                                    filter(Order.pay_status == 2).\
                                    order_by(Order.order_id.desc()).limit(10).all()
    orders = []
    for order in goods_orders:
        status_text, action_code = OrderStaticMethodsService.order_status_text_and_action_code(order)
        order                    = kt_to_dict(order)
        order['status_text']     = status_text
        orders.append(order)

    goods_orders_amount = 0
    for goods_order in goods_orders:
        goods_orders_amount += goods_order.order_amount

    #最近评论
    comments           = db.session.query(Comment.nickname, Comment.avatar, Comment.add_time, 
                                        Comment.rating, Comment.content, Comment.img_data).\
                                        order_by(Comment.comment_id.desc()).limit(4).all()
                                        
    data = {'sum_user':sum_user, 
            'sum_order':sum_order, 
            'sum_order_amount':sum_order_amount, 
            'sum_aftersales':sum_aftersales, 
            'fund_orders_amount':fund_orders_amount,
            'funds_orders':funds_orders,
            'orders':orders,
            'orders_amount':goods_orders_amount,
            'comments':comments
            }
            
    return render_template('admin/dashboard/index.html.j2', **data)
    

@index.route('/success')
def success():
    """操作成功反馈页面"""
    return render_template('admin/success.html.j2')


@index.route('/signout')
def signout():
    """退出登录"""
    session.clear()
    return redirect('admin/auth/login')
    