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

from app.services.response import ResponseJson
from app.services.api.like import LikeService

from app.models.like import Like


like = Blueprint('api.like', __name__)

resjson = ResponseJson()
resjson.module_code = 10

@like.route('/action')
def action():
    """ 点赞或取消点赞 """
    resjson.action_code = 10

    # ??
    #check_login()

    args      = request.args
    like_type = toint(args.get('like_type', 0))
    ttype     = toint(args.get('ttype', 0))
    tid       = toint(args.get('tid', 0))
    
    ls = LikeService(like_type, ttype, tid)
    if not ls.check():
        return resjson.print_json(10, ls.msg)

    ls.action()
    ls.commit()

    return resjson.print_json(0, u'ok', {'action_code':ls.action_code})
