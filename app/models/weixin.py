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

class WeixinMpTemplate(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'weixin_mp_template'

    wmt_id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=0)
