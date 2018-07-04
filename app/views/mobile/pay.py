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

pay = Blueprint('mobile.pay', __name__)


@pay.route('/success/<int:order_id>')
def success(order_id):
    """手机站 - 完成支付"""

    return render_template('mobile/pay/success.html.j2', order_id=order_id)
