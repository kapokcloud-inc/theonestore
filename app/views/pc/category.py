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
    Blueprint,
    url_for
)

from app.helpers import (
    render_template,
    log_info,
    toint
)

from app.services.api.item import (
    CategoryService,
    ItemListService
)


category = Blueprint('pc.category', __name__)

@category.route('/')
@category.route('/<int:cat_id>')
@category.route('/<int:cat_id>/')
def root(cat_id = 0):
    """分类页"""
    if cat_id == 0:
        categories = CategoryService().categories()
        return render_template('pc/category/index.html.j2', categories=categories)

    args = request.args
    p = toint(args.get('p', '1'))

    cat_service = CategoryService()
    cat = cat_service.get_category(cat_id)

    service = ItemListService(p, 20, cat_id)
    items = service.items()

    return render_template('pc/item/index.html.j2',
                category = cat,
                items = items,
                pagination = service.pagination)
