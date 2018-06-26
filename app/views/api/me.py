# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
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

from app.forms.api.me import AddressForm

from app.models.like import Like


me = Blueprint('api.me', __name__)

resjson = ResponseJson()
resjson.module_code = 13

@me.route('/address/save', methods=["POST"])
def address_save():
    """保存地址"""
    resjson.action_code = 10

    # ??
    #if not check_login():
    #    return resjson.print_json(10, _(u'未登陆'))
    #uid = get_uid()
    uid = 1

    wtf_form           = AddressForm()
    _current_timestamp = current_timestamp()

    if not wtf_form.validate_on_submit():
        log_info(dir(wtf_form.errors))
        log_info(wtf_form.errors)
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    return resjson.print_json(0, u'ok')
