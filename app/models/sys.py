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

class SysSetting(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'sys_setting'

    ss_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), default='')
    value = db.Column(db.Text, default=None)
    desc = db.Column(db.String(225), default='')


class SysToken(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'sys_token'

    st_id = db.Column(db.Integer, primary_key=True)
    token_type = db.Column(db.String(20), default='')
    access_token = db.Column(db.String(255), default='')
    expires_in = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)
