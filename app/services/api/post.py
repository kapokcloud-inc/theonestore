# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from app.database import db

from app.helpers import (
    log_info,
    toint,
)

from app.models.post import (
    Post,
    PostCategories
)


class PostStaticMethodsService(object):
    """文章静态类方法是"""

    @staticmethod
    def categories():
        """文章分类列表"""
        categories = db.session.query(PostCategories.cat_id, PostCategories.cat_name).\
                                    filter(PostCategories.is_show == 1).\
                                     order_by(PostCategories.sorting.desc()).\
                                     order_by(PostCategories.cat_id.desc()).all()

        return categories
    
    @staticmethod
    def posts(cat_id = 0):
        """获取指定分类文章列表"""
        q = db.session.query(Post.post_id, Post.post_name).\
                            filter(Post.is_publish == 1).\
                            order_by(Post.sorting.desc()).\
                            order_by(Post.post_id.desc())

        if cat_id > 0:
            q = q.filter(Post.cat_id == cat_id)
        
        posts = q.all()

        return posts
    
    @staticmethod
    def post_detail(post_id = 0):
        """获取文章详情"""
        if post_id <= 0:
            return None

        post = db.session.query(Post.post_id, Post.post_name, 
                            Post.cat_id, Post.cat_name, Post.post_detail).\
                            filter(Post.is_publish == 1).\
                            filter(Post.post_id == post_id).first()
        return post

