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
from sqlalchemy import or_, and_

from app.database import db

from app.helpers import (
    render_template,
    log_info,
    get_count
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_nickname,
    get_avatar
)

from app.services.message import MessageStaticMethodsService
from app.services.api.like import LikeStaticMethodsService

from app.forms.api.me import (
    AddressForm
)

from app.models.aftersales import Aftersales
from app.models.message import Message
from app.models.order import (
    Order,
    OrderGoods
)
from app.models.funds import Funds
from app.models.coupon import Coupon
from app.models.user import (
    User,
    UserAddress,
    UserLastTime
)


me = Blueprint('pc.me', __name__)

@me.route('/')
def index():
    """pc站 - 个人中心"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid          = get_uid()
    nickname     = get_nickname()
    avatar       = get_avatar()
    current_time = current_timestamp()

    # 优惠券
    q = Coupon.query.\
            filter(Coupon.uid == uid).\
            filter(Coupon.is_valid == 1).\
            filter(Coupon.begin_time <= current_time).\
            filter(Coupon.end_time >= current_time)
    coupon_count = get_count(q)

    # 未付款订单
    q = db.session.query(Order.order_id).\
            filter(Order.uid == uid).\
            filter(Order.is_remove == 0).\
            filter(Order.order_status == 1).\
            filter(Order.pay_status == 1)
    unpaid_count = get_count(q)

    # 待收货订单
    q = db.session.query(Order.order_id).\
            filter(Order.uid == uid).\
            filter(Order.is_remove == 0).\
            filter(Order.order_status == 1).\
            filter(Order.pay_status == 2).\
            filter(Order.deliver_status.in_([0,1]))
    undeliver_count = get_count(q)

    completed = db.session.query(Order.order_id).\
                    filter(Order.uid == uid).\
                    filter(Order.is_remove == 0).\
                    filter(Order.order_status == 2).\
                    filter(Order.pay_status == 2).\
                    filter(Order.deliver_status == 2).all()
    completed = [order.order_id for order in completed]

    # 待评价
    q = db.session.query(OrderGoods.og_id).\
            filter(OrderGoods.order_id.in_(completed)).\
            filter(OrderGoods.comment_id == 0)
    uncomment_count = get_count(q)

    # 退款售后
    q = db.session.query(Aftersales.aftersales_id).\
            filter(Aftersales.status.in_([1,2]))
    aftersales_count = get_count(q)

    # 未读消息
    ult          = UserLastTime.query.filter(UserLastTime.uid == uid).filter(UserLastTime.last_type == 1).first()
    last_time    = ult.last_time if ult else 0
    unread_count = get_count(db.session.query(Message.message_id).filter(Message.tuid == uid).filter(Message.add_time > last_time))

    funds = Funds.query.filter(Funds.uid == uid).first()

    data = {'uid':uid, 'nickname':nickname, 'avatar':avatar, 'coupon_count':coupon_count,
            'unpaid_count':unpaid_count, 'undeliver_count':undeliver_count, 'uncomment_count':uncomment_count,
            'aftersales_count':aftersales_count, 'unread_count':unread_count, 'funds':funds}
    return render_template('pc/me/index.html.j2', **data)


@me.route('/addresses')
def addresses():
    """pc站 - 收货地址"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    addresses = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.is_default.desc()).all()

    return render_template('pc/me/addresses.html.j2', addresses=addresses)


@me.route('/collect')
def collect():
    """pc站 - 我的收藏"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data      = LikeStaticMethodsService.likes({'uid':uid})

    return render_template('pc/me/collect.html.j2', likes=data['likes'])


@me.route('/coupon')
def coupon():
    """pc站 - 我的优惠券"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid          = get_uid()
    current_time = current_timestamp()

    q = Coupon.query.\
            filter(Coupon.uid == uid).\
            filter(Coupon.is_valid == 1).\
            filter(Coupon.begin_time <= current_time).\
            filter(Coupon.end_time >= current_time)
    valid_count   = get_count(q)
    valid_coupons = q.order_by(Coupon.coupon_id.desc()).all()

    q = Coupon.query.\
            filter(Coupon.uid == uid).\
            filter(or_(and_(Coupon.is_valid == 0, Coupon.order_id == 0), Coupon.end_time < current_time))
    invalid_count   = get_count(q)
    invalid_coupons = q.order_by(Coupon.coupon_id.desc()).all()
    
    q = Coupon.query.\
            filter(Coupon.uid == uid).\
            filter(Coupon.order_id > 0)
    used_count   = get_count(q)
    used_coupons = q.order_by(Coupon.coupon_id.desc()).all()

    data = {'valid_coupons':valid_coupons, 'invalid_coupons':invalid_coupons, 'used_coupons':used_coupons,
            'valid_count':valid_count, 'invalid_count':invalid_count, 'used_count':used_count}
    return render_template('pc/me/coupon.html.j2', **data)


@me.route('/messages')
def messages():
    """pc站 - 消息通知"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    messages   = MessageStaticMethodsService.messages({'uid':uid})

    return render_template('pc/me/messages.html.j2', messages=messages)
