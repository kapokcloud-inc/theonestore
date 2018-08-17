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

pay = Blueprint('pc.pay', __name__)


@pay.route('/success/<int:order_id>')
def success(order_id):
    """pc站 - 支付成功"""

    return render_template('pc/pay/success.html.j2', order_id=order_id)


@pay.route('/recharge_success')
def recharge_success():
    """pc站 - 充值成功"""

    return render_template('pc/pay/recharge_success.html.j2')
