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

from app.helpers import (
    render_template,
    log_info
)

from app.services.api.item import CategoryService


category = Blueprint('pc.category', __name__)

@category.route('/')
@category.route('/<int:cat_id>')
@category.route('/<int:cat_id>/')
def root(cat_id = 0):
    """分类页"""
    categories = CategoryService().categories()
    return render_template('pc/category/index.html.j2', categories=categories)
