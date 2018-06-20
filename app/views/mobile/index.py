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

from app.services.api.item import ItemStaticMethodsService

from app.models.adv import Adv


index = Blueprint('mobile.index', __name__)

@index.route('/')
def root():
    """手机站 - 首页"""

    advs = db.session.query(Adv.adv_id, Adv.img, Adv.ttype, Adv.tid, Adv.url).\
        filter(Adv.ac_id == 1).\
        filter(Adv.is_show == 1).\
        order_by(Adv.sorting.desc(), Adv.adv_id.desc()).all()
    
    hot_items       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    recommend_items = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})

    return render_template('mobile/index/index.html.j2', advs=advs, hot_items=hot_items, recommend_items=recommend_items)

