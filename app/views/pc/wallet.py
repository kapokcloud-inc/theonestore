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

from app.services.api.funds import FundsStaticMethodsService

from app.models.order import Order
from app.models.funds import (
    Funds,
    FundsDetail
)

wallet = Blueprint('pc.wallet', __name__)


@wallet.route('/')
def root():
    """pc站 - 我的钱包"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    funds   = Funds.query.filter(Funds.uid == uid).first()
    details = FundsStaticMethodsService.details(uid, {})

    return render_template('pc/wallet/index.html.j2', funds=funds, details=details)


@wallet.route('/recharge')
def recharge():
    """pc站 - 钱包充值"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    order_id        = toint(request.args.get('order_id', '0'))
    is_weixin       = toint(request.args.get('is_weixin', '0'))
    recharge_amount = 0
    redirect_url    = url_push_query(request.url, 'is_weixin=1')

    # 订单付款
    if order_id > 0:
        # 检查
        order = Order.query.filter(Order.order_id == order_id).filter(Order.uid == uid).first()
        if not order:
            return redirect(request.headers['Referer'])
        
        recharge_amount = order.pay_amount

    data = {'order_id':order_id, 'recharge_amount':recharge_amount, 'is_weixin':is_weixin, 'redirect_url':redirect_url}
    return render_template('pc/wallet/recharge.html.j2', **data)