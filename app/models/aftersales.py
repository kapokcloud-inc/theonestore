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

class Aftersales(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'aftersales'

    aftersales_id = db.Column(db.Integer, primary_key=True)
    aftersales_sn = db.Column(db.String(25), default='')
    uid = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, default=0)
    aftersales_type = db.Column(db.Integer, default=0)
    deliver_status = db.Column(db.Integer, default=0)
    content = db.Column(db.String(255), default='')
    img_data = db.Column(db.Text, default=None)
    status = db.Column(db.Integer, default=0)
    check_status = db.Column(db.Integer, default=0)
    check_content = db.Column(db.String(255), default='')
    refunds_id = db.Column(db.Integer, default=0)
    refunds_amount = db.Column(db.Float, default=0.00)
    refunds_method = db.Column(db.String(16), default='')
    refunds_sn = db.Column(db.String(25), default='')
    refunds_status = db.Column(db.Integer, default=0)
    return_shipping_name = db.Column(db.String(32), default='')
    return_shipping_sn = db.Column(db.String(32), default='')
    return_status = db.Column(db.Integer, default=0)
    resend_shipping_name = db.Column(db.String(32), default='')
    resend_shipping_sn = db.Column(db.String(32), default='')
    resend_status = db.Column(db.Integer, default=0)
    latest_log = db.Column(db.String(255), default='')
    goods_data = db.Column(db.Text, default=None)
    quantity = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class AftersalesAddress(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'aftersales_address'

    aa_id = db.Column(db.Integer, primary_key=True)
    aftersales_id = db.Column(db.Integer, default=0)
    name = db.Column(db.String(32), default='')
    mobile = db.Column(db.String(15), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    district = db.Column(db.String(32), default='')
    address = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class AftersalesGoods(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'aftersales_goods'

    ag_id = db.Column(db.Integer, primary_key=True)
    aftersales_id = db.Column(db.Integer, default=0)
    og_id = db.Column(db.Integer, default=0)
    goods_id = db.Column(db.Integer, default=0)
    goods_name = db.Column(db.String(255), default='')
    goods_img = db.Column(db.String(255), default='')
    goods_desc = db.Column(db.String(255), default='')
    goods_quantity = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)


class AftersalesLogs(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'aftersales_logs'

    al_id = db.Column(db.Integer, primary_key=True)
    aftersales_id = db.Column(db.Integer, default=0)
    content = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
