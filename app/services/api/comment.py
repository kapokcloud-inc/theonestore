# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp

from app.models.comment import Comment


class CommentStaticMethodsService(object):
    """评论静态方法Service"""

    @staticmethod
    def comments(params):
        """获取评论列表"""

        p      = toint(params.get('p', '1'))
        ps     = toint(params.get('ps', '10'))
        ttype  = toint(params.get('ttype', '0'))
        tid    = toint(params.get('tid', '0'))
        rating = toint(params.get('rating', '0'))
        is_img = toint(params.get('is_img', '0'))

        q = db.session.query(Comment.comment_id, Comment.uid, Comment.nickname, Comment.avatar,
                                Comment.rating, Comment.content, Comment.img_data, Comment.add_time).\
                filter(Comment.ttype == ttype).\
                filter(Comment.tid == tid).\
                filter(Comment.is_show == 1)

        if rating in ([1,2,3]):
            q = q.filter(Comment.rating == rating)
        
        if is_img == 1:
            q = q.filter(Comment.img_data != '[]')

        comments = q.order_by(Comment.comment_id.desc()).offset((p-1)*ps).limit(ps).all()

        return comments
