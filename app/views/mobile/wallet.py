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

wallet = Blueprint('mobile.wallet', __name__)


@wallet.route('/')
def root():
    """手机站 - 我的钱包"""
    return render_template('mobile/wallet/index.html.j2')


@wallet.route('/recharge')
def recharge():
    """手机站 - 钱包充值"""
    return render_template('mobile/wallet/recharge.html.j2')


@wallet.route('/detail')
def detail():
    """手机站 - 交易明细详情"""
    return render_template('mobile/wallet/detail.html.j2')
