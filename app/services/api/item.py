# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _

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
    """ 商品静态方法Service """

    @staticmethod
    def items(args):
        """ 获取商品列表 """
        
        cat_id = toint(args.get('cat_id', '0'))
        p      = toint(args.get('p', '1'))
        ps     = toint(args.get('ps', '10'))

        q = db.session.query(Goods.goods_id, Goods.goods_name, Goods.goods_img, Goods.goods_desc,
                                Goods.goods_price, Goods.market_price).\
            filter(Goods.is_delete == 0).\
            filter(Goods.is_sale == 1).\
            filter(Goods.stock_quantity > 0)

        if cat_id > 0:
            q = q.filter(Goods.cat_id == cat_id)

        items = q.order_by(Goods.goods_id.desc()).offset((p-1)*ps).limit(ps).all()

        return items

