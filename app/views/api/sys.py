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
from flask_wtf.csrf import generate_csrf

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.models.sys import SysSetting
from app.services.response import ResponseJson
from app.services.sms import SmsServiceFactory
from app.exception import SmsException

sys = Blueprint('api.sys', __name__)

resjson = ResponseJson()
resjson.module_code = 22

@sys.route('/csrf-token', methods=['GET'])
def csrf_token():
    """获取csrf_token"""
    resjson.action_code = 10

    csrf_token = generate_csrf()

    return resjson.print_json(0, u'ok', {'csrf_token': csrf_token})
