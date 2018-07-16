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

class Message(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True)
    message_type = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='')
    content = db.Column(db.String(255), default='')
    data = db.Column(db.Text, default=None)
    fuid = db.Column(db.Integer, default=0)
    fname = db.Column(db.String(32), default='')
    favatar = db.Column(db.String(128), default='')
    tuid = db.Column(db.Integer, default=0)
    tname = db.Column(db.String(32), default='')
    tavatar = db.Column(db.String(128), default='')
    tid = db.Column(db.Integer, default=0)
    ttype = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    add_date = db.Column(db.Integer, default=0)
