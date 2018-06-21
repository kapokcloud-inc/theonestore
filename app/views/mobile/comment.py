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

comment = Blueprint('mobile.comment', __name__)


@comment.route('/<int:goods_id>')
def goods(goods_id):
    """手机站 - 商品评论"""
    return render_template('mobile/comment/goods.html.j2')

