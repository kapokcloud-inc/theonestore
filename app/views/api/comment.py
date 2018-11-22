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
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _

from app.database import db
from app.services.response import ResponseJson

from app.helpers import (
    render_template,
    toint
)

from app.services.api.comment import CommentStaticMethodsService

from app.models.comment import Comment


comment = Blueprint('api.comment', __name__)

resjson = ResponseJson()
resjson.module_code = 23

@comment.route('/index')
def index():
    """ 评论列表 """
    resjson.action_code = 10

    params = request.args.to_dict()
    
    p      = toint(params.get('p', '1'))
    ps     = toint(params.get('ps', '10'))
    ttype  = toint(params.get('ttype', '0'))
    tid    = toint(params.get('tid', '0'))
    rating = toint(params.get('rating', '0'))
    is_img = toint(params.get('is_img', '0'))
    
    if p <=0 or ps <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    if ttype not in [0, 1] or tid <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)
    
    if rating not in [0, 1, 2, 3]:
        return resjson.print_json(resjson.PARAM_ERROR)
    
    if is_img not in [0 ,1]:
        return resjson.print_json(resjson.PARAM_ERROR)

    dataIndex = CommentStaticMethodsService.index_page(request.args)
    data = CommentStaticMethodsService.comments(params)

    data['rating_1_count'] = dataIndex['rating_1_count']
    data['rating_2_count'] = dataIndex['rating_2_count']
    data['rating_3_count'] = dataIndex['rating_3_count']
    data['img_count'] = dataIndex['img_count']

    return resjson.print_json(0, u'ok', data)