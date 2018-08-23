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

class Comment(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'comment'

    comment_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(255), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=3)
    content = db.Column(db.Text, default=None)
    img_data = db.Column(db.Text, default=None)
    is_show = db.Column(db.Integer, default=1)
    add_time = db.Column(db.Integer, default=0)
