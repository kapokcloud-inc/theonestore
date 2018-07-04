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
    toint,
    get_count
)

from app.services.api.comment import CommentStaticMethodsService

from app.models.comment import Comment


comment = Blueprint('mobile.comment', __name__)

@comment.route('/')
def index():
    """手机站 - 商品评论"""

    comments   = CommentStaticMethodsService.comments(request.args.to_dict())
    paging_url = url_for('mobile.comment.paging', **request.args)

    ttype  = toint(request.args.get('ttype', '0'))
    tid    = toint(request.args.get('tid', '0'))
    rating = toint(request.args.get('rating', '0'))
    is_img = toint(request.args.get('is_img', '0'))

    q = db.session.query(Comment.comment_id).filter(Comment.ttype == ttype).filter(Comment.tid == tid).filter(Comment.is_show == 1)
    rating_1_count = get_count(q.filter(Comment.rating == 1))

    q = db.session.query(Comment.comment_id).filter(Comment.ttype == ttype).filter(Comment.tid == tid).filter(Comment.is_show == 1)
    rating_2_count = get_count(q.filter(Comment.rating == 2))

    q = db.session.query(Comment.comment_id).filter(Comment.ttype == ttype).filter(Comment.tid == tid).filter(Comment.is_show == 1)
    rating_3_count = get_count(q.filter(Comment.rating == 3))

    q = db.session.query(Comment.comment_id).filter(Comment.ttype == ttype).filter(Comment.tid == tid).filter(Comment.is_show == 1)
    img_count = get_count(q.filter(Comment.img_data != '[]'))

    data = {'comments':comments, 'paging_url':paging_url, 'rating_1_count':rating_1_count, 'rating_2_count':rating_2_count,
            'rating_3_count':rating_3_count, 'img_count':img_count, 'tid':tid, 'rating':rating, 'is_img':is_img}
    return render_template('mobile/comment/index.html.j2', **data)


@comment.route('/paging')
def paging():
    """加载分页"""

    comments = CommentStaticMethodsService.comments(request.args.to_dict())

    return render_template('mobile/comment/paging.html.j2', comments=comments)
