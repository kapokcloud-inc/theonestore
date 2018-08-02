# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from app.views import pc

PC_ROUTES = (
    (pc.index,          ''),
    (pc.category,       '/pc/category'),
    (pc.item,           '/pc/item'),
    (pc.cart,           '/pc/cart'),
    (pc.order,          '/pc/order'),
    (pc.aftersales,     '/pc/aftersales'),
    (pc.pay,            '/pc/pay'),
    (pc.me,             '/pc/me'),
)
