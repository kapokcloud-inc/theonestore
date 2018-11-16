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
from app.services.api.user import UserStaticMethodsService
from app.services.api.me import MeStaticMethodsService

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
from app.models.item import Goods
from app.models.like import Like
from app.models.user import (
    User,
    UserAddress
)


me = Blueprint('pc.me', __name__)

@me.route('/')
def index():
    """pc站 - 个人中心"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid  = get_uid()
    
    data = MeStaticMethodsService.detail(uid)
    #用户信息
    user = User.query.get(uid)

    # 收藏商品
    q = db.session.query(Like.like_id).\
            filter(Like.uid == uid).\
            filter(Like.like_type == 2).\
            filter(Like.ttype == 1)
    collect_count = get_count(q)

    wtf_form = ProfileForm()
    
    data['user']          = user
    data['collect_count'] = collect_count
    data['wtf_form']      = wtf_form

    return render_template('pc/me/index.html.j2', **data)


@me.route('/addresses')
def addresses():
    """pc站 - 收货地址"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    addresses = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.is_default.desc()).all()
    wtf_form  = AddressForm()

    return render_template('pc/me/addresses.html.j2', addresses=addresses, wtf_form=wtf_form)


@me.route('/collect')
def collect():
    """pc站 - 我的收藏"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid           = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    data          = LikeStaticMethodsService.likes(params,True)

    goods         = {}
    for like in data["likes"]:
        good            = db.session.query(Goods.goods_price,Goods.market_price).filter(Goods.goods_id == like.tid).first()
        goods[like.tid] = good

    data['goods'] = goods
    return render_template('pc/me/collect.html.j2', **data)


@me.route('/coupon')
def coupon():
    """pc站 - 我的优惠券"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
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
    """pc站 - 消息通知列表"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    data          = MessageStaticMethodsService.messages(params,True)

    UserStaticMethodsService.reset_last_time(uid, 1)

    return render_template('pc/me/messages.html.j2', **data)


@me.route('/signout')
def signout():
    """退出登录"""

    session.clear()

    return redirect(url_for('pc.index.root'))
