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
