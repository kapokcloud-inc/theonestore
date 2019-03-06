# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _


class TheonestoreException(Exception):
    """ 一店异常 """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ConfigNotFoundException(TheonestoreException):
    """ 配置不存在异常 """
    def __init__(self, msg=_(u'配置不存在')):
        TheonestoreException.__init__(self, msg)


class ParamNotFoundException(TheonestoreException):
    """ 参数不存在异常 """
    def __init__(self, msg=_(u'参数不存在')):
        TheonestoreException.__init__(self, msg)


class NetworkException(TheonestoreException):
    """ 网络异常 """
    def __init__(self, msg=_(u'网络异常')):
        TheonestoreException.__init__(self, msg)


class UserException(TheonestoreException):
    """用户异常"""
    def __init__(self, msg=_(u'用户不存在')):
        TheonestoreException.__init__(self, msg)


class AddressException(TheonestoreException):
    def __init__(self, msg=_(u'地址不存在')):
        TheonestoreException.__init__(self, msg)


class OrderException(TheonestoreException):
    def __init__(self, msg=_(u'订单不存在')):
        TheonestoreException.__init__(self, msg)


class CouponException(TheonestoreException):
    def __init__(self, msg=_(u'优惠券不存在')):
        TheonestoreException.__init__(self, msg)


class GoodsException(TheonestoreException):
    def __init__(self, msg=_(u'商品不存在')):
        TheonestoreException.__init__(self, msg)
