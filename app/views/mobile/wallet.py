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

from app.helpers import (
    render_template,
    log_info,
    toint,
    url_push_query
)
from app.helpers.user import (
    check_login,
    get_uid
)
from app.helpers.date_time import (
    current_timestamp
)

from app.services.api.funds import FundsStaticMethodsService

from app.models.order import Order
from app.models.funds import (
    Funds,
    FundsDetail
)

wallet = Blueprint('mobile.wallet', __name__)


@wallet.route('/')
def root():
    """手机站 - 我的钱包"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    funds      = Funds.query.filter(Funds.uid == uid).first()
    _data      = FundsStaticMethodsService.details(uid, {})
    paging_url = url_for('mobile.wallet.paging', **request.args)

    data = {'funds':funds, 'details':_data['details'], 'paging_url':paging_url}
    return render_template('mobile/wallet/index.html.j2', **data)


@wallet.route('/paging')
def paging():
    """加载分页"""

    if not check_login():
        session['weixin_login_url'] = url_for('mobile.wallet.root')
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    _data = FundsStaticMethodsService.details(uid, request.args.to_dict())

    return render_template('mobile/wallet/paging.html.j2', details=_data['details'])


@wallet.route('/recharge')
def recharge():
    """手机站 - 钱包充值"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_id        = toint(request.args.get('order_id', '0'))
    recharge_amount = 0

    # 订单付款
    if order_id > 0:
        # 检查
        order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
        if not order:
            return redirect(request.headers['Referer'])
        
        recharge_amount = order.pay_amount

    openid             = ''
    opentime           = session.get('jsapi_weixin_opentime', 0)
    current_time       = current_timestamp()
    is_expire_opentime = opentime < (current_time-30*60)
    if not is_expire_opentime:
        openid = session.get('jsapi_weixin_openid', '')

    pay_success_url = url_for('mobile.pay.success', order_id=order_id)

    data = {'order_id':order_id, 'recharge_amount':recharge_amount,
            'openid':openid, 'pay_success_url':pay_success_url}
    return render_template('mobile/wallet/recharge.html.j2', **data)


@wallet.route('/detail/<int:fd_id>')
def detail(fd_id):
    """手机站 - 交易明细详情"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    detail = FundsDetail.query.filter(FundsDetail.fd_id == fd_id).filter(FundsDetail.uid == uid).first()
    if not detail:
        return redirect(request.headers['Referer'])

    return render_template('mobile/wallet/detail.html.j2', detail=detail)
