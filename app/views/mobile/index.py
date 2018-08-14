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
from app.services.api.adv import AdvStaticMethodsService

from app.models.adv import Adv


index = Blueprint('mobile.index', __name__)

@index.route('/')
def root():
    """手机站 - 首页"""

    advs           = AdvStaticMethodsService.advs({'ac_id':1}, platform_type=1)
    data_hot       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    data_recommend = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})

    data = {'advs':advs, 'hot_items':data_hot['items'], 'recommend_items':data_recommend['items']}
    return render_template('mobile/index/index.html.j2', **data)

