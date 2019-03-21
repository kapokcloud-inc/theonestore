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
    url_for,
    abort
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


category = Blueprint('mobile.category', __name__)

@category.route('/')
@category.route('/<int:cat_id>')
@category.route('/<int:cat_id>/')
def root(cat_id=0):
    """分类页"""
    if cat_id == 0:
        categories = CategoryService().categories()
        return render_template('mobile/category/index.html.j2', categories=categories)
    
    ps = 10
    p = toint(request.args.get('p', '1'))
    cat = CategoryService().get_category(cat_id)
    if cat is None:
        return abort(404)

    service = ItemListService(p, ps, cat_id)
    return render_template('mobile/item/index.html.j2', 
                items = service.items(),
                pagination = service.pagination,
                category = cat,
                paging_url = url_for('mobile.item.paging', cat_id=cat_id))
