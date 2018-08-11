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

from app.database import db

from app.helpers import (
    log_info,
    toint,
    model_update
)

from app.services.api.comment import CommentStaticMethodsService

from app.models.comment import Comment
from app.models.like import Like
from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


class ItemStaticMethodsService(object):
    """商品静态方法Service"""

    @staticmethod
    def items(params, is_pagination=False):
        """获取商品列表"""

        p            = toint(params.get('p', '1'))
        ps           = toint(params.get('ps', '10'))
        cat_id       = toint(params.get('cat_id', '0'))
        is_hot       = toint(params.get('is_hot', '-1'))
        is_recommend = toint(params.get('is_recommend', '-1'))

        q = db.session.query(Goods.goods_id, Goods.goods_name, Goods.goods_img, Goods.goods_desc,
                                Goods.goods_price, Goods.market_price).\
            filter(Goods.is_delete == 0).\
            filter(Goods.is_sale == 1).\
            filter(Goods.stock_quantity > 0)

        category = None
        if cat_id > 0:
            q        = q.filter(Goods.cat_id == cat_id)
            category = GoodsCategories.query.get(cat_id)
        
        if is_hot in [0,1]:
            q = q.filter(Goods.is_hot == is_hot)

        if is_recommend in [0,1]:
            q = q.filter(Goods.is_recommend == is_recommend)

        items = q.order_by(Goods.goods_id.desc()).offset((p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        return {'items':items, 'category':category, 'pagination':pagination}

    @staticmethod
    def categories():
        """获取商品分类列表"""

        categories = db.session.query(GoodsCategories.cat_id,
                                        GoodsCategories.cat_name,
                                        GoodsCategories.cat_img).\
                            filter(GoodsCategories.is_show == 1).\
                            order_by(GoodsCategories.sorting.desc()).\
                            order_by(GoodsCategories.cat_id.desc()).all()
       
        return categories

    @staticmethod
    def detail_page(goods_id, uid):
        """商品详情页"""

        item      = Goods.query.get_or_404(goods_id)
        galleries = db.session.query(GoodsGalleries.img).\
                        filter(GoodsGalleries.goods_id == goods_id).all()

        is_fav = None
        if uid:
            is_fav = db.session.query(Like.like_id).\
                        filter(Like.like_type == 2).\
                        filter(Like.ttype == 1).\
                        filter(Like.tid == goods_id).\
                        filter(Like.uid == uid).first()
        is_fav = 1 if is_fav else 0

        comments = []
        pagination = None
        if item.comment_count > 0:
            params     = {'p':1, 'ps':12, 'ttype':1, 'tid':goods_id}
            data       = CommentStaticMethodsService.comments(params, is_pagination=True)
            comments   = data['comments']
            pagination = data['pagination']

        model_update(item, {'view_count':item.view_count+1}, commit=True)

        q = db.session.query(Comment.comment_id).\
                filter(Comment.ttype == 1).\
                filter(Comment.tid == goods_id).\
                filter(Comment.is_show == 1)

        rating_1_count = q.filter(Comment.rating == 1).count()
        rating_2_count = q.filter(Comment.rating == 2).count()
        rating_3_count = q.filter(Comment.rating == 3).count()
        img_count      = q.filter(Comment.img_data != '[]').count()

        data = {'item':item, 'galleries':galleries, 'is_fav':is_fav,
                'comments':comments, 'rating_1_count':rating_1_count,
                'rating_2_count':rating_2_count, 'rating_3_count':rating_3_count,
                'img_count':img_count, 'pagination':pagination}
        return data
