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

from app.services.response import ResponseJson
from app.services.api.item import CategoryService


category = Blueprint('api.category', __name__)

resjson = ResponseJson()
resjson.module_code = 18

@category.route('/')
def root():
    """ 分类列表 """
    resjson.action_code = 10
    categories = CategoryService().categories()
    return resjson.print_json(0, u'ok', {'category':categories})
