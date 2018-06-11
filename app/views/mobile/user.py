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

from app.helpers import render_template

user = Blueprint('mobile.user', __name__)


@user.route('/')
def root():
    """手机站 - 个人中心"""
    return render_template('mobile/user/index.html.j2')


@user.route('/info')
def info():
    """手机站 - 修改用户信息"""
    return render_template('mobile/user/user_info.html.j2')


@user.route('/address')
def address():
    """手机站 - 收货地址管理"""
    return render_template('mobile/user/delivery_address.html.j2')


@user.route('/add')
def add():
    """手机站 - 收货地址管理"""
    return render_template('mobile/user/add_address.html.j2')


@user.route('/collect')
def collect():
    """手机站 - 我的收藏"""
    return render_template('mobile/user/collect.html.j2')


@user.route('/coupon')
def coupon():
    """手机站 - 我的优惠券"""
    return render_template('mobile/user/coupon.html.j2')


@user.route('/order')
def order():
    """手机站 - 我的订单"""
    return render_template('mobile/user/order.html.j2')


@user.route('/order/detail')
def order_detail():
    """手机站 - 订单详情"""
    return render_template('mobile/user/order_detail.html.j2')


@user.route('/messages')
def messages():
    """手机站 - 消息"""
    return render_template('mobile/user/messages.html.j2')


@user.route('/review')
def review():
    """手机站 - 发表评价"""
    return render_template('mobile/user/review.html.j2')


@user.route('/settlement')
def settlement():
    """手机站 - 提交订单"""
    return render_template('mobile/user/settlement.html.j2')
