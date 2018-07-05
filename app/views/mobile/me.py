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

from app.helpers import (
    render_template,
    get_count
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid,
    get_nickname,
    get_avatar
)

from app.forms.api.me import ProfileForm

from app.models.funds import Funds
from app.models.coupon import Coupon
from app.models.user import User


me = Blueprint('mobile.me', __name__)

@me.route('/')
def index():
    """手机站 - 个人中心"""

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

    funds = Funds.query.filter(Funds.uid == uid).first()

    data = {'uid':uid, 'nickname':nickname, 'avatar':avatar, 'coupon_count':coupon_count, 'funds':funds}
    return render_template('mobile/me/index.html.j2', **data)


@me.route('/profile')
def profile():
    """手机站 - 修改用户信息"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()
    
    user     = User.query.get(uid)
    wtf_form = ProfileForm()

    return render_template('mobile/me/profile.html.j2', user=user, wtf_form=wtf_form)


@me.route('/address')
def address():
    """手机站 - 收货地址管理"""
    return render_template('mobile/user/delivery_address.html.j2')


@me.route('/add')
def add():
    """手机站 - 收货地址管理"""
    return render_template('mobile/user/add_address.html.j2')


@me.route('/collect')
def collect():
    """手机站 - 我的收藏"""
    return render_template('mobile/user/collect.html.j2')


@me.route('/coupon')
def coupon():
    """手机站 - 我的优惠券"""

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
    return render_template('mobile/me/coupon.html.j2', **data)


@me.route('/messages')
def messages():
    """手机站 - 消息"""
    return render_template('mobile/user/messages.html.j2')


@me.route('/review')
def review():
    """手机站 - 发表评价"""
    return render_template('mobile/user/review.html.j2')