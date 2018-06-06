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

cart = Blueprint('mobile.cart', __name__)


@cart.route('/')
def root():
    """手机站 - 我的购物车"""
    return render_template('mobile/cart/index.html.j2')


@cart.route('/edit')
def edit():
    """手机站 - 购物车编辑"""
    return render_template('mobile/cart/cart_edit.html.j2')
