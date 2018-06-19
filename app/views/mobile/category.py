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

category = Blueprint('mobile.category', __name__)


@category.route('/')
def root():
    """手机站 - 分类页"""
    return render_template('mobile/category/index.html.j2')


@category.route('/page')
def page():
    """手机站 - 分类商品页"""
    return render_template('mobile/category/page.html.j2')


@category.route('/product/detail')
def product_detail():
    """手机站 - 商品详情页"""
    return render_template('mobile/category/product_detail.html.j2')
