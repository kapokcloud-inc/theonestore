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
    ml_to_dl
)

from app.services.response import ResponseJson

from app.services.api.item import ItemStaticMethodsService

item = Blueprint('api.item', __name__)

resjson = ResponseJson()
resjson.module_code = 11

@item.route('/goods')
def goods():
    """ 商品列表分页 """
    resjson.action_code = 10
    log_info(request.args.to_dict())
    items = ItemStaticMethodsService.items(request.args.to_dict(), False)
    
    return resjson.print_json(0, u'ok', {'goods':items})
