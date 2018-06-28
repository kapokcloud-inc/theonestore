# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask import (
    Blueprint,
    request
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.response import ResponseJson
from app.services.api.order import OrderCreateService

from app.models.order import Order


order = Blueprint('api.order', __name__)

resjson = ResponseJson()
resjson.module_code = 14

@order.route('/create', methods=['POST'])
def create():
    """ 创建订单 """
    resjson.action_code = 10

    # ??
    #if not check_login():
    #    return resjson.print_json(10, _(u'未登陆'))
    #uid = get_uid()
    uid = 1

    form = request.form
    carts_id   = form.get('carts_id', '').strip()
    ua_id      = toint(form.get('ua_id', '0'))
    shpping_id = toint(form.get('shipping_id', '0'))
    coupon_id  = toint(form.get('coupon_id', '0'))

    carts_id = carts_id.split(',')
    carts_id = [toint(cart_id) for cart_id in carts_id]

    ocs = OrderCreateService(uid, carts_id, ua_id, shpping_id, coupon_id)
    if not ocs.check():
        return resjson.print_json(11, ocs.msg)

    ocs.create()

    return resjson.print_json(0, u'ok', {'order':ocs.order})
