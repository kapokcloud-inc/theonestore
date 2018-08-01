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

from app.helpers import (
    render_template,
    toint
)

from app.services.api.comment import CommentStaticMethodsService

from app.models.comment import Comment


comment = Blueprint('mobile.comment', __name__)

@comment.route('/')
def index():
    """手机站 - 商品评论"""

    data               = CommentStaticMethodsService.index_page(request.args.to_dict())
    data['paging_url'] = url_for('mobile.comment.paging', **request.args)

    return render_template('mobile/comment/index.html.j2', **data)


@comment.route('/paging')
def paging():
    """加载分页"""

    comments = CommentStaticMethodsService.comments(request.args.to_dict())

    return render_template('mobile/comment/paging.html.j2', comments=comments)
