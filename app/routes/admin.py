# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.views import admin

ADMIN_ROUTES = (
    (admin.index,       '/admin'),
    (admin.auth,        '/admin/auth'),
    (admin.config,      '/admin/config'),
    # (admin.item,        '/admin/item'),
    # (admin.order,       '/admin/order'),
    # (admin.recharge,    '/admin/recharge'),
    # (admin.coupon,      '/admin/coupon'),
    # (admin.adv,         '/admin/adv'),
    # (admin.aftersale,   '/admin/aftersale'),
    (admin.user,        '/admin/user'),
    # (admin.comment,     '/admin/comment'),
    # (admin.post,        '/admin/post'),
    (admin.upload,      '/admin/upload')
)
