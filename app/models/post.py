# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.database import db
from app.models import BaseModel

class Post(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True)
    post_name = db.Column(db.String(32), default='')
    post_detail = db.Column(db.Text, default=None)
    cat_id = db.Column(db.Integer, default=0)
    cat_name = db.Column(db.String(32), default='')
    is_publish = db.Column(db.Integer,default=0)
    sorting = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class PostCategories(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'post_categories'

    cat_id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(32), default='')
    is_show = db.Column(db.Integer,default=0)
    sorting = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    