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
    url_for,
    g
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db
from app.helpers import (
    render_template,
    log_info,
    toint,
    model_update
)
from app.helpers.date_time import date_range

from app.services.response import ResponseJson

from app.models.item import Goods
from app.models.comment import Comment


comment = Blueprint('admin_comment', __name__)

resjson = ResponseJson()
resjson.module_code = 19

@comment.route('/index')
@comment.route('/index/<int:page>')
@comment.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """评论列表"""
    g.page_title = _(u'商品评价')

    args               = request.args
    goods_id           = toint(args.get('goods_id', '0'))
    add_time_daterange = args.get('add_time_daterange', '').strip()

    q = db.session.query(Comment.comment_id, Comment.uid, Comment.nickname, Comment.avatar,
                            Comment.rating, Comment.content, Comment.img_data, Comment.add_time,
                            Goods.goods_id, Goods.goods_name, Goods.goods_img).\
                        filter(Comment.tid == Goods.goods_id).\
                        filter(Comment.ttype == 1).\
                        filter(Comment.is_show == 1)

    if goods_id > 0:
        q = q.filter(Comment.tid == goods_id)

    if add_time_daterange:
        start, end = date_range(add_time_daterange)
        q          = q.filter(Comment.add_time >= start).filter(Comment.add_time < end)

    comments   = q.order_by(Comment.comment_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/comment/index.html.j2', pagination=pagination, comments=comments)


@comment.route('/remove')
def remove():
    """删除评论"""
    resjson.action_code = 10

    comment_id = toint(request.args.get('comment_id', '0'))

    if comment_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    comment = Comment.query.get(comment_id)
    if not comment:
        return resjson.print_json(10, _(u'评论不存在'))

    if comment.is_show == 0:
        return resjson.print_json(0, u'ok')

    model_update(comment, {'is_show':0}, commit=True)

    return resjson.print_json(0, u'ok')
