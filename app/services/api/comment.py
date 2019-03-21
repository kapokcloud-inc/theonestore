# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db

from app.helpers import (
    log_info,
    toint,
    get_count
)
from app.helpers.date_time import current_timestamp

from app.models.comment import Comment


class CommentService(object):
    """评论Service"""

    def __init__(self, tid, ttype=0, rating=0, is_img=False):
        """
        :param int tid 第三方id，如：商品id
        :param int ttype 评论类型，默认为0
        :param int rating 1:差评 2:中评 3:好评
        :param boolean is_img 是否有图
        """
        self.tid = tid
        self.ttype = ttype
        self.rating = rating
        self.is_img = is_img
        self.queryobj = None


    @property
    def query(self):
        """获取查询对象
        :param int page 页码
        :param int page_size 每页数据量
        :param int rating 1:差评 2:中评 3:好评
        :param boolean is_img 是否有图
        """
        if self.queryobj is not None:
            return self.queryobj

        q = db.session.query(
                    Comment.comment_id, 
                    Comment.uid, 
                    Comment.nickname, 
                    Comment.avatar,
                    Comment.rating, 
                    Comment.content, 
                    Comment.img_data, 
                    Comment.add_time).\
                filter(Comment.ttype == self.ttype).\
                filter(Comment.tid == self.tid).\
                filter(Comment.is_show == 1)
        if self.rating in (1,2,3):
            q = q.filter(Comment.rating == self.rating)
        if self.is_img is True:
            q = q.filter(Comment.img_data != '[]')
        
        self.queryobj = q
        return self.queryobj


    def comments(self, page, page_size):
        """获取评论列表
        :param int page 页码
        :param int page_size 每页数据量
        """
        comments = self.query.order_by(Comment.comment_id.desc()).\
                        offset((page-1)*page_size).\
                        limit(page_size).all()
        return comments

    
    def get_pagination(self, page, page_size):
        """获取分页对象
        :param int page 页码
        :param int page_size 每页数据量
        """
        pagination = Pagination(None, page, page_size, self.query.count(), None)
        return pagination


class CommentStaticMethodsService(object):
    """评论静态方法Service"""

    @staticmethod
    def comments(params, is_pagination=False):
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

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        return {'comments':comments, 'pagination':pagination}

    @staticmethod
    def index_page(args):
        """评论首页"""

        data             = args.to_dict()
        _data            = CommentStaticMethodsService.comments(data)
        data['comments'] = _data['comments']

        ttype  = toint(data.get('ttype', '0'))
        tid    = toint(data.get('tid', '0'))

        q = db.session.query(Comment.comment_id).\
                filter(Comment.ttype == ttype).\
                filter(Comment.tid == tid).\
                filter(Comment.is_show == 1)

        data['rating_1_count'] = get_count(q.filter(Comment.rating == 1))
        data['rating_2_count'] = get_count(q.filter(Comment.rating == 2))
        data['rating_3_count'] = get_count(q.filter(Comment.rating == 3))
        data['img_count']      = get_count(q.filter(Comment.img_data != '[]'))

        return data
