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
    (pc.category,       '/category'),
    (pc.item,           '/item'),
    (pc.cart,           '/cart'),
    (pc.order,          '/order'),
    (pc.aftersales,     '/aftersales'),
    (pc.pay,            '/pay'),
    (pc.me,             '/me'),
    (pc.wallet,         '/wallet'),
    (pc.post,           '/post'),
)
