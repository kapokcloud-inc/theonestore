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
    json
)

from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
)

from app.services.api.item import ItemStaticMethodsService
from app.services.api.adv import AdvStaticMethodsService

from app.services.response import ResponseJson

index = Blueprint('api.index', __name__)

resjson = ResponseJson()
resjson.module_code = 19

@index.route('/home')
def home():
    """首页"""
    resjson.action_code = 10
    
    advs           = AdvStaticMethodsService.advs({'ac_id':1}, platform_type=1)
    data_hot       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    data_recommend = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})

    data = {'advs':advs, 'hot_items':data_hot['items'], 'recommend_items':data_recommend['items']}
    return resjson.print_json(0, u'ok', data)
