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

class Coupon(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'coupon'

    coupon_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    cb_id = db.Column(db.Integer, default=0)
    coupon_name = db.Column(db.String(255), default='')
    begin_time = db.Column(db.Integer, default=0)
    end_time = db.Column(db.Integer, default=0)
    is_valid = db.Column(db.Integer, default=0)
    limit_amount = db.Column(db.Float, default=99999.00)
    coupon_amount = db.Column(db.Float, default=0.00)
    limit_goods = db.Column(db.String(255), default='')
    limit_goods_name = db.Column(db.String(255), default='')
    coupon_from = db.Column(db.String(16), default='')
    order_id = db.Column(db.Integer, default=0)
    use_time = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)


class CouponBatch(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'coupon_batch'

    cb_id = db.Column(db.Integer, primary_key=True)
    cb_name = db.Column(db.String(255), default='')
    coupon_name = db.Column(db.String(100), default=None)
    begin_time = db.Column(db.Integer, default=0)
    end_time = db.Column(db.Integer, default=0)
    is_valid = db.Column(db.Integer, default=0)
    publish_num = db.Column(db.Integer, default=0)
    give_num = db.Column(db.Integer, default=0)
    use_num = db.Column(db.Integer, default=0)
    limit_amount = db.Column(db.Float, default=9999.00)
    coupon_amount = db.Column(db.Float, default=0.00)
    limit_goods = db.Column(db.String(255), default='')
    limit_goods_name = db.Column(db.String(255), default='')
    date_num = db.Column(db.Integer, default=0)
    coupon_from = db.Column(db.String(16), default='')
    valid_days = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)
