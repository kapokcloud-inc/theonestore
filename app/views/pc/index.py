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

from app.helpers import render_template

from app.services.api.item import ItemStaticMethodsService

from app.models.adv import Adv


index = Blueprint('pc.index', __name__)


@index.route('/')
def root():
    """pc - 首页"""

    advs = db.session.query(Adv.adv_id, Adv.img, Adv.ttype, Adv.tid, Adv.url).\
        filter(Adv.ac_id == 1).\
        filter(Adv.is_show == 1).\
        order_by(Adv.sorting.desc(), Adv.adv_id.desc()).all()

    hot_items, pagination       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    recommend_items, pagination = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})


    data = {'advs':advs, 'hot_items':hot_items, 'recommend_items':recommend_items}
    return render_template('pc/index/index.html.j2', **data)
