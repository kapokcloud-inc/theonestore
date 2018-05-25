# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.database import db


class BaseModel(object):
    """基础model类"""

    def __str__(self):
        info = self.__dict__.copy()
        info.pop('_sa_instance_state')
        return u"%s" % (info, )

    __repr__ = __str__


    

