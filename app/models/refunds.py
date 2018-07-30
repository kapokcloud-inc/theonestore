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

class Refunds(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'refunds'

    refunds_id = db.Column(db.Integer, primary_key=True)
    tran_id = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    refunds_amount = db.Column(db.Float, default=0.00)
    refunds_method = db.Column(db.String(16), default='')
    refunds_sn = db.Column(db.String(25), default='')
    refunds_time = db.Column(db.Integer, default=0)
    refunds_status = db.Column(db.Integer, default=0)
    remark_user = db.Column(db.String(255), default='')
    remark_sys = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
