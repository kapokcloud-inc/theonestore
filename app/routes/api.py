# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.views import api

API_ROUTES = (
    (api.like,      '/api/like'),
    (api.weixin,    '/api/weixin'),
    (api.cart,      '/api/cart'),
    (api.me,        '/api/me'),
    (api.order,     '/api/order'),
    (api.pay,       '/api/pay')
)
