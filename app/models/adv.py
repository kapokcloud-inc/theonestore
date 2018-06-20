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

class Adv(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'adv'

    adv_id = db.Column(db.Integer, primary_key=True)
    ac_id = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='')
    desc = db.Column(db.String(255), default='')
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    url = db.Column(db.String(255), default='')
    sorting = db.Column(db.Integer, default=0)
    is_show = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)

