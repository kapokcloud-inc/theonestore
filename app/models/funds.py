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

class Funds(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'funds'

    uid = db.Column(db.Integer, primary_key=True)
    funds = db.Column(db.Float, default=0.00)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class FundsDetail(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'funds_detail'

    fd_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    funds_prev = db.Column(db.Float, default=0.00)
    funds_change = db.Column(db.Float, default=0.00)
    funds = db.Column(db.Float, default=0.00)
    event = db.Column(db.Integer, default=0)
    ttype = db.Column(db.Integer, default=0)
    tid = db.Column(db.Integer, default=0)
    remark_user = db.Column(db.String(255), default='')
    remark_sys = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
