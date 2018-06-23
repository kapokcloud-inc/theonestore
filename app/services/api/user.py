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
    model_create,
    model_update,
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp

from app.models.user import User


class UserCreateService(object):
    """创建用户Service"""

    def __init__(self, user_data, current_time=0, request=None):
        self.msg          = u''
        self.user         = None
        self.user_data    = {}
        self.current_time = current_time if current_time else current_timestamp()

        _user_data_key = ['nickname', 'avatar', 'gender', 'country', 'province', 'city']
        for key in _user_data_key:
            self.user_data[key] = user_data.get(key, '')

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def check(self):
        """检查"""

        self.user_data['gender']      = 0 if self.user_data['gender'] == '' else self.user_data['gender']
        self.user_data['add_time']    = self.current_time
        self.user_data['update_time'] = self.current_time

        return True

    def create(self):
        """创建"""

        self.user = model_create(User, self.user_data)
