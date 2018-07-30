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
    toint
)

from app.models.item import (
    Goods,
    GoodsCategories,
    GoodsGalleries
)


class ItemStaticMethodsService(object):
    """商品静态方法Service"""

    @staticmethod
    def items(params):
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

        if cat_id > 0:
            q = q.filter(Goods.cat_id == cat_id)
        
        if is_hot in [0,1]:
            q = q.filter(Goods.is_hot == is_hot)

        if is_recommend in [0,1]:
            q = q.filter(Goods.is_recommend == is_recommend)

        items      = q.order_by(Goods.goods_id.desc()).offset((p-1)*ps).limit(ps).all()
        pagination = Pagination(None, p, ps, q.count(), None)

        return (items, pagination)

    @staticmethod
    def categories(params):
        """获取商品分类列表"""

        categories = db.session.query(GoodsCategories.cat_id,
                                        GoodsCategories.cat_name,
                                        GoodsCategories.cat_img).\
                            filter(GoodsCategories.is_show == 1).\
                            order_by(GoodsCategories.sorting.desc()).\
                            order_by(GoodsCategories.cat_id.desc()).all()

        return categories
