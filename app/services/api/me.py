# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import session
from flask_babel import gettext as _
from sqlalchemy import or_, and_

from app.database import db

from app.helpers import (
    log_info,
    get_count
)

from app.helpers.user import (
    get_uid,
    get_nickname,
    get_avatar
)
from app.helpers.date_time import current_timestamp

from app.services.message import MessageStaticMethodsService
from app.services.api.like import LikeStaticMethodsService
from app.services.api.user import UserStaticMethodsService

from app.forms.api.me import (
    ProfileForm,
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
    UserAddress
)

class MeStaticMethodsService(object):
    """ 我的页面静态Service """

    @staticmethod
    def detail(uid):
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
                filter(Order.order_type == 1).\
                filter(Order.is_remove == 0).\
                filter(Order.order_status == 1).\
                filter(Order.pay_status == 1)
        unpaid_count = get_count(q)

        # 待收货订单
        q = db.session.query(Order.order_id).\
                filter(Order.uid == uid).\
                filter(Order.order_type == 1).\
                filter(Order.is_remove == 0).\
                filter(Order.order_status == 1).\
                filter(Order.pay_status == 2).\
                filter(Order.deliver_status.in_([0,1]))
        undeliver_count = get_count(q)

        completed = db.session.query(Order.order_id).\
                        filter(Order.uid == uid).\
                        filter(Order.order_type == 1).\
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
                filter(Aftersales.status.in_([1,2])).\
                filter(Aftersales.uid == uid)
        aftersales_count = get_count(q)

        funds = Funds.query.filter(Funds.uid == uid).first()

        data = {'uid':uid, 'nickname':nickname, 'avatar':avatar, 'coupon_count':coupon_count,
                'unpaid_count':unpaid_count, 'undeliver_count':undeliver_count, 'uncomment_count':uncomment_count,
                'aftersales_count':aftersales_count, 'funds':funds}
        
        return data
