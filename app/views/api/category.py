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

from app.services.response import ResponseJson

from app.services.api.item import ItemStaticMethodsService


category = Blueprint('api.category', __name__)

resjson = ResponseJson()
resjson.module_code = 18

@category.route('/')
def root():
    """ 分类列表 """
    resjson.action_code = 10

    categories = ItemStaticMethodsService.categories()
    
    return resjson.print_json(0, u'ok', {'category':categories})
