# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

class ConfigNotExistException(Exception):
    """配置不存在异常"""
    
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


