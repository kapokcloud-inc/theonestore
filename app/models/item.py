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

class Goods(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'goods'

    goods_id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, default=0)
    goods_name = db.Column(db.String(255), default='')
    goods_img = db.Column(db.String(255), default='')
    goods_desc = db.Column(db.String(255), default='')
    goods_price = db.Column(db.Float, default=0.00)
    market_price = db.Column(db.Float, default=0.00)
    detail = db.Column(db.Text, default=None)
    is_sale = db.Column(db.Integer, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    sold_quantity = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    is_delete = db.Column(db.Integer, default=0)
    is_hot = db.Column(db.Integer, default=0)
    is_recommend = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)
    update_time = db.Column(db.Integer, default=None)


class GoodsCategories(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'goods_categories'

    cat_id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(32), default='')
    cat_img = db.Column(db.String(255), default='')
    parent_id = db.Column(db.Integer, default=0)
    sorting = db.Column(db.Integer, default=0)
    is_show = db.Column(db.Integer, default=0)
    add_time = db.Column(db.Integer, default=0)


class GoodsGalleries(BaseModel, db.Model):
    __bind_key__ = 'theonestore'
    __tablename__ = 'goods_galleries'

    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255), default='')
    add_time = db.Column(db.Integer, default=0)
