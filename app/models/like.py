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

class Like(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'like'

    like_id = db.Column(db.Integer, primary_key=True)
    like_type = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(255), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    tname = db.Column(db.String(255), default='')
    timg = db.Column(db.String(255), default='')
    ext_data = db.Column(db.Text, default=None)
    add_time = db.Column(db.Integer, default=0)
