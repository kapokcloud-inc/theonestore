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

from app.database import db

from app.helpers import (
    render_template,
    log_info
)

from app.services.api.item import ItemStaticMethodsService

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


category = Blueprint('pc.category', __name__)

@category.route('/')
def root():
    """pc - 分类页"""

    categories = db.session.query(GoodsCategories.cat_id, GoodsCategories.cat_name, GoodsCategories.cat_img).\
        filter(GoodsCategories.is_show == 1).order_by(GoodsCategories.sorting.desc(), GoodsCategories.cat_id.desc()).all()

    return render_template('pc/category/index.html.j2', categories=categories)
