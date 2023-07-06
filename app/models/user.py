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

class User(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'user'

    uid = db.Column(db.Integer, primary_key=True)
    # uuid = db.Column(db.String(50), default='')
    nickname = db.Column(db.String(32), default='')
    avatar = db.Column(db.String(255), default='')
    gender = db.Column(db.Integer, default=0)
    country = db.Column(db.String(32), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11), default='')
    email = db.Column(db.String(50), default='')


class UserAddress(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'user_address'

    ua_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    name = db.Column(db.String(32), default='')
    mobile = db.Column(db.String(15), default='')
    province = db.Column(db.String(32), default='')
    city = db.Column(db.String(32), default='')
    district = db.Column(db.String(32), default='')
    address = db.Column(db.String(255), default='')
    zip = db.Column(db.String(8), default='')
    is_default = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class UserThirdBind(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'user_third_bind'

    utb_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    third_type = db.Column(db.Integer, default=0)
    third_user_id = db.Column(db.String(255), default='')
    third_unionid = db.Column(db.String(255), default='')
    third_res_text = db.Column(db.Text, default=None)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)


class UserLastTime(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'user_last_time'

    ult_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, default=0)
    last_type = db.Column(db.Integer, default=0)
    last_time = db.Column(db.Integer, default=0)
