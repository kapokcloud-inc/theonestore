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
from app.models.user import (
    User,
    UserAddress
)


me = Blueprint('mobile.me', __name__)

@me.route('/')
def index():
    """手机站 - 个人中心"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid          = get_uid()

    data = MeStaticMethodsService.detail(uid)
    return render_template('mobile/me/index.html.j2', **data)


@me.route('/profile')
def profile():
    """手机站 - 修改用户信息"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()
    
    user     = User.query.get(uid)
    wtf_form = ProfileForm()

    return render_template('mobile/me/profile.html.j2', user=user, wtf_form=wtf_form)


@me.route('/addresses')
def addresses():
    """手机站 - 收货地址管理"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    addresses = UserAddress.query.filter(UserAddress.uid == uid).order_by(UserAddress.is_default.desc()).all()

    return render_template('mobile/me/addresses.html.j2', addresses=addresses)


@me.route('/address/<int:ua_id>')
def address(ua_id):
    """手机站 - 添加收货地址"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    address = {}
    if ua_id > 0:
        address = UserAddress.query.filter(UserAddress.ua_id == ua_id).filter(UserAddress.uid == uid).first()
        if not address:
            return redirect(url_for('mobile.index.pagenotfound'))

    wtf_form = AddressForm()

    return render_template('mobile/me/address.html.j2', ua_id=ua_id, address=address, wtf_form=wtf_form)


@me.route('/collect')
def collect():
    """手机站 - 我的收藏"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data       = LikeStaticMethodsService.likes({'uid':uid})
    paging_url = url_for('mobile.me.collect_paging', **request.args)

    return render_template('mobile/me/collect.html.j2', likes=data['likes'], paging_url=paging_url)


@me.route('/collect-paging')
def collect_paging():
    """我的收藏 - 加载分页"""

    if not check_login():
        session['weixin_login_url'] = url_for('mobile.me.collect')
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    data          = LikeStaticMethodsService.likes(params)

    return render_template('mobile/me/collect_paging.html.j2', likes=data['likes'])


@me.route('/coupon')
def coupon():
    """手机站 - 我的优惠券"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid  = get_uid()
    
    data = MeStaticMethodsService.coupons(uid)

    return render_template('mobile/me/coupon.html.j2', **data)


@me.route('/messages')
def messages():
    """手机站 - 消息"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data       = MessageStaticMethodsService.messages({'uid':uid})
    paging_url = url_for('mobile.me.messages_paging', **request.args)

    UserStaticMethodsService.reset_last_time(uid, 1)

    return render_template('mobile/me/messages.html.j2', messages=data["messages"], paging_url=paging_url)


@me.route('/messages-paging')
def messages_paging():
    """消息 - 加载分页"""

    if not check_login():
        session['weixin_login_url'] = url_for('mobile.me.messages')
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    data          = MessageStaticMethodsService.messages(params)

    return render_template('mobile/me/messages_paging.html.j2', messages=data["messages"])


@me.route('/signout')
def signout():
    """退出登录"""

    session.clear()

    return redirect(url_for('mobile.index.root'))
