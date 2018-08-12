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

from app.models.message import Message
from app.models.user import (
    User,
    UserLastTime
)


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


class UserStaticMethodsService(object):
    """用户静态方法Service"""

    @staticmethod
    def create_account(uid, is_commit=False):
        """创建帐户"""

        model_create(UserLastTime, {'uid':uid, 'last_type':1, 'last_time':0}, commit=is_commit)

        return True

    @staticmethod
    def unread_count(uid):
        """未读消息数"""

        ult          = UserLastTime.query.\
                            filter(UserLastTime.uid == uid).\
                            filter(UserLastTime.last_type == 1).first()
        last_time    = ult.last_time if ult else 0
        unread_count = db.session.query(Message.message_id).\
                            filter(Message.tuid == uid).\
                            filter(Message.add_time > last_time).count()

        return unread_count

    @staticmethod
    def reset_last_time(uid, last_type):
        """重置最新时间"""

        current_time = current_timestamp()

        ult = UserLastTime.query.\
                filter(UserLastTime.uid == uid).\
                filter(UserLastTime.last_type == last_type).first()

        model_update(ult, {'last_time':current_time}, commit=True)

        return True
