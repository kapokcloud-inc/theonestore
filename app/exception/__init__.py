# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
class TheonestoreException(Exception):
    """ 一店异常 """

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg

class ConfigNotFoundException(TheonestoreException):
    """ 配置不存在异常 """

    def __init__(self, msg=u'配置不存在'):
        TheonestoreException.__init__(self, msg)

class ParamNotFoundException(TheonestoreException):
    """ 参数不存在异常 """

    def __init__(self, msg=u'参数不存在'):
        TheonestoreException.__init__(self, msg)

class NetworkException(TheonestoreException):
    """ 网络异常 """

    def __init__(self, msg=u'网络异常'):
        TheonestoreException.__init__(self, msg)