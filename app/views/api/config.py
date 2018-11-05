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
    toint
)
from app.models.sys import SysSetting
from app.services.response import ResponseJson

config = Blueprint('api.config', __name__)

resjson = ResponseJson()
resjson.module_code = 21

@config.route('/base', methods=['GET'])
def base():
    """微信_基本信息"""
    resjson.action_code = 10
    
    ss = SysSetting.query.filter(SysSetting.key == 'config_info_base').first()
    if not ss:
        return resjson.print_json(11, u'请先配置应用基本信息')
    base = {}
    try:
        base = json.loads(ss.value)
    except Exception as e:
        return resjson.print_json(12, u'应用基本信息格式化失败')

    data = {'base_info': base}
    return resjson.print_json(0, u'ok', data)