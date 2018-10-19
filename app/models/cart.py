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

class Cart(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    session_id = db.Column(db.String(190), default='')
    goods_id = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    is_checked = db.Column(db.Integer, default=1)
    checkout_type = db.Column(db.Integer, default=1)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)
