# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from app.views import mobile

MOBILE_ROUTES = (
    (mobile.index,          '/mobile'),
    (mobile.category,       '/mobile/category'),
    (mobile.cart,           '/mobile/cart'),
    (mobile.item,           '/mobile/item'),
    (mobile.comment,        '/mobile/comment'),
    (mobile.pay,            '/mobile/pay'),
    (mobile.wallet,         '/mobile/wallet'),
    (mobile.order,          '/mobile/order'),
    (mobile.aftersales,     '/mobile/aftersales'),
    (mobile.me,             '/mobile/me')
)
