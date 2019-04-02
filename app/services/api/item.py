# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination
from flask import session

from app.database import db

from app.helpers import (
    log_info,
    toint,
    get_count,
    model_update
)
from app.models.cart import Cart
from app.models.comment import Comment
from app.models.like import Like
from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)
from app.services.api.comment import CommentService


class CategoryService(object):
    """分类service"""

    def categories(self, is_recommend=False):
        """获取所有分类列表"""
        q = db.session.query(
            GoodsCategories.cat_id,
            GoodsCategories.cat_name,
            GoodsCategories.cat_img
        ).filter(GoodsCategories.is_show == 1)
        if is_recommend is True:
            q = q.filter(GoodsCategories.is_recommend == 1)

        return q.order_by(GoodsCategories.sorting.desc()).\
            order_by(GoodsCategories.cat_id.desc()).all()

    def get_category(self, cat_id):
        """获取分类信息"""
        return GoodsCategories.query.get(cat_id)


class ItemService(object):
    """商品service"""

    def __init__(self, goods_id, uid=0):
        self.goods_id = goods_id
        self.uid = uid
        self.cs = CommentService(self.goods_id)

    @property
    def item(self):
        """商品信息"""
        return Goods.query.get_or_404(self.goods_id)

    @property
    def galleries(self):
        """相册"""
        return db.session.query(GoodsGalleries.img).\
            filter(GoodsGalleries.goods_id == self.goods_id).all()

    @property
    def is_fav(self):
        """收藏"""
        if self.uid == 0:
            return 0

        fav = db.session.query(Like.like_id).\
            filter(Like.like_type == 2).\
            filter(Like.ttype == 1).\
            filter(Like.tid == self.goods_id).\
            filter(Like.uid == self.uid).first()
        return 1 if fav is not None else 0

    def comments(self, page, page_size):
        """评论列表"""
        return self.cs.comments(page, page_size)

    def comment_pagination(self, page, page_size):
        """评论分页对象"""
        return self.cs.get_pagination(page, page_size)

    def get_rating_count(self, rating):
        """获取评价总数
        :param int rating 1:差评 2:中评 3:好评
        """
        if rating in (1, 2, 3):
            q = self.cs.query.filter(Comment.rating == rating)
            return get_count(q)
        return 0

    def get_image_rating_count(self):
        """获取有图评价总数"""
        q = self.cs.query.filter(Comment.img_data != '[]')
        return get_count(q)

    def cart_num(self):
        """购物车商品数"""

        q = Cart.query.filter(Cart.goods_id == self.goods_id).filter(
            Cart.checkout_type == 1)
        if self.uid:
            q = q.filter(Cart.uid == self.uid)
        else:
            q = q.filter(Cart.session_id == session.sid)
        cart = q.first()
        if not cart:
            return 0
        return cart.quantity


class ItemListService(object):
    """商品列表service"""

    def __init__(self, page, page_size=10, cat_id=0, is_hot=0, is_recommend=0, search_key=''):
        # 页码
        self.page = page

        # 每页记录数
        self.page_size = page_size

        # 分类id
        self.cat_id = cat_id

        # 是否热门
        self.is_hot = is_hot

        # 是否推荐
        self.is_recommend = is_recommend

        # 搜索关键词
        self.search_key = search_key

        # 查询sqlalchemy对象
        self.query = None

    def _query(self):
        """获取query对象"""
        if self.query is not None:
            return self.query

        q = db.session.query(
            Goods.goods_id,
            Goods.goods_name,
            Goods.goods_img,
            Goods.goods_desc,
            Goods.goods_price,
            Goods.market_price).\
            filter(Goods.is_delete == 0).\
            filter(Goods.is_sale == 1).\
            filter(Goods.stock_quantity > 0)
        if self.cat_id > 0:
            q = q.filter(Goods.cat_id == self.cat_id)
        if self.is_hot == 1:
            q = q.filter(Goods.is_hot == self.is_hot)
        if self.is_recommend == 1:
            q = q.filter(Goods.is_recommend == self.is_recommend)
        if self.search_key:
            q = q.filter(Goods.goods_name.like(u'%%'+self.search_key+u'%%'))

        self.query = q
        return self.query

    def items(self):
        """获取商品列表"""
        q = self._query()
        return q.order_by(Goods.goods_id.desc()).\
            offset((self.page-1)*self.page_size).limit(self.page_size).all()

    @property
    def pagination(self):
        """分页对象"""
        q = self._query()
        return Pagination(None, self.page, self.page_size, get_count(q), None)
