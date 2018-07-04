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

class Order(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    order_sn = db.Column(db.String(25), default='')
    tran_id = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer, default=0)
    order_type = db.Column(db.Integer, default=0)
    order_status = db.Column(db.Integer, default=0)
    goods_amount = db.Column(db.Float, default=0.00)
    order_amount = db.Column(db.Float, default=0.00)
    discount_amount = db.Column(db.Float, default=0.00)
    discount_desc = db.Column(db.String(255), default='')
    pay_amount = db.Column(db.Float, default=0.00)
    pay_method = db.Column(db.String(16), default='')
    pay_type = db.Column(db.Integer, default=0)
    pay_status = db.Column(db.Integer, default=0)
    pay_tran_id = db.Column(db.String(32), default='')
    paid_time = db.Column(db.Integer, default=0)
    paid_amount = db.Column(db.Float, default=0.00)
    shipping_id = db.Column(db.Integer, default=0)
    shipping_name = db.Column(db.String(32), default='')
    shipping_code = db.Column(db.String(20), default='')
    shipping_amount = db.Column(db.Float, default=0.00)
    free_limit_amount = db.Column(db.Float, default=0.00)
    shipping_sn = db.Column(db.String(32), default='')
    shipping_status = db.Column(db.Integer, default=0)
    shipping_time = db.Column(db.Integer, default=0)
    deliver_status = db.Column(db.Integer, default=0)
    deliver_time = db.Column(db.Integer, default=0)
    cancel_status = db.Column(db.Integer, default=0)
    cancel_desc = db.Column(db.String(255), default='')
    cancel_time = db.Column(db.Integer, default=0)
    is_remove = db.Column(db.Integer, default=0)
    order_desc = db.Column(db.String(255), default='')
    user_remark = db.Column(db.Text, default=None)
    is_comment = db.Column(db.Integer, default=0)
    goods_quantity = db.Column(db.Integer, default=0)
    goods_data = db.Column(db.Text, default=None)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class OrderAddress(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order_address'

    oa_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(32), default='')
    mobile = db.Column(db.String(15), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    district = db.Column(db.String(32), default='')
    address = db.Column(db.String(255), default='')
    zip = db.Column(db.String(8), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class OrderGoods(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order_goods'

    og_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    goods_name = db.Column(db.String(255), default='')
    goods_img = db.Column(db.String(255), default='')
    goods_quantity = db.Column(db.Integer, default=0)
    goods_price = db.Column(db.Float, default=0.00)
    comment_id = db.Column(db.Integer, default=0)
    service_valid_time = db.Column(db.Integer, default=0)
    service_goods_quantity = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class OrderIndex(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order_index'

    order_id = db.Column(db.Integer, primary_key=True)


class OrderTran(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order_tran'

    tran_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    pay_amount = db.Column(db.Float, default=0.00)
    pay_status = db.Column(db.Integer, default=0)
    pay_method = db.Column(db.String(16), default='')
    pay_tran_id = db.Column(db.String(32), default='')
    paid_time = db.Column(db.Integer, default=0)
    order_id_list = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class OrderTranIndex(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'order_tran_index'

    tran_id = db.Column(db.Integer, primary_key=True)
