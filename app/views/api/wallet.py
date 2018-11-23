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
)
from flask_babel import gettext as _

from app.helpers import (
    log_info,
    toint,
)
from app.helpers.user import (
    check_login,
    get_uid
)
from app.helpers.date_time import (
    current_timestamp
)
from app.services.response import ResponseJson
from app.services.api.funds import FundsStaticMethodsService

from app.models.order import Order
from app.models.funds import (
    Funds,
    FundsDetail
)

wallet = Blueprint('api.wallet', __name__)

resjson = ResponseJson()
resjson.module_code = 24

@wallet.route('/')
def index():
    """ 我的钱包 """

    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    args = request.args
    p = toint(args.get('p', '1'))
    ps = toint(args.get('ps', '10'))

    if p <= 0 or ps <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    funds      = Funds.query.filter(Funds.uid == uid).first()
    _data      = FundsStaticMethodsService.details(uid, request.args.to_dict())

    data = {'funds':funds, 'details':_data['details']}
    return resjson.print_json(0, u'ok', data)

@wallet.route('/detail')
def detail():
    """ 交易明细详情 """

    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    fd_id = toint(request.args.get('fd_id', '0'))
    if fd_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    detail = FundsDetail.query.filter(FundsDetail.fd_id == fd_id).filter(FundsDetail.uid == uid).first()

    if not detail:
        return resjson.print_json(10, _(u'交易明细不存在'))

    return resjson.print_json(0, u'ok', {'detail': detail})