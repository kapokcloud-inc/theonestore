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


class Shipping(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'shipping'

    shipping_id = db.Column(db.Integer, primary_key=True)
    shipping_name = db.Column(db.String(32), default='')
    shipping_amount = db.Column(db.Float, default=0.00)
    shipping_desc = db.Column(db.String(255), default='')
    free_limit_amount = db.Column(db.Float, default=0.00)
    shipping_code = db.Column(db.String(20), default='')
    aggreate_code = db.Column(db.String(20), default='')
    is_enable = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Integer, default=0)
    sorting = db.Column(db.Integer, default=0)
