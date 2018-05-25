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

class AdminUsers(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'admin_users'

    admin_uid = db.Column(db.Integer, primary_key=True)
    admin_gid = db.Column(db.Integer, default=0)
    login_name = db.Column(db.String(128), default='')
    mobile = db.Column(db.String(15), default='')
    display_name = db.Column(db.String(32), default='')
    salt = db.Column(db.String(64), default='')
    password = db.Column(db.String(256), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=None)

