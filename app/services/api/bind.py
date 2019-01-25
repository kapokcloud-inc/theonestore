# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask_babel import gettext as _

from app.helpers import (
    log_info,
    model_create,
    model_update
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import set_user_session

from app.services.api.user import (
    UserCreateService,
    UserStaticMethodsService
)

from app.models.user import User, UserThirdBind


class BindService(object):
    """第三方登录绑定Service"""

    def __init__(self, third_type, third_user_id, third_unionid, third_res_text, user_data, current_time=0):
        self.msg            = u''
        self.third_type     = third_type        # 绑定类型: 0.默认; 1.微信公众号; 2.微信扫码; 3.微信小程序;
        self.third_user_id  = third_user_id     # 第三方平台用户ID
        self.third_unionid  = third_unionid     # 第三方平台用户联合ID
        self.third_res_text = third_res_text    # 第三方平台返回TEXT
        self.user_data      = user_data         # 用户个人信息
        self.current_time   = current_time if current_time else current_timestamp()

    def __check(self):
        """检查"""

        if self.third_type not in [1, 2, 3]:
            self.msg = _(u'绑定类型错误')
            return False

        if not self.third_user_id and not self.third_unionid:
            self.msg = _(u'绑定ID错误')
            return False

        if not isinstance(self.user_data, dict) and not self.user_data['nickname'] and not self.user_data['avatar']:
            self.msg = _(u'用户个人信息错误')
            return False

        return True

    def bind(self):
        """绑定"""

        if not self.__check():
            return False

        # 查询是否已绑定
        utb = UserThirdBind.query.\
                    filter(UserThirdBind.third_type == self.third_type).\
                    filter(UserThirdBind.third_user_id == self.third_user_id).first()

        # 查询是否已绑定
        if not utb:
            utb = UserThirdBind.query.\
                    filter(UserThirdBind.third_type == self.third_type).\
                    filter(UserThirdBind.third_unionid == self.third_unionid).first()

        if not utb:
            ucs = UserCreateService(self.user_data, self.current_time)
            if not ucs.check():
                return False

            # 创建用户
            ucs.create()
            ucs.commit()
            user = ucs.user

            # 创建帐户
            UserStaticMethodsService.create_account(user.uid, self.current_time, is_commit=False)

            # 创建绑定
            data = {'uid':user.uid, 'third_type':self.third_type,
                    'third_user_id':self.third_user_id, 'third_unionid':self.third_unionid,
                    'third_res_text':json.dumps(self.third_res_text), 'add_time':self.current_time}
            utb  = model_create(UserThirdBind, data)
        else:
            user = User.query.get(utb.uid)
            if not user:
                return False

        model_update(utb, {'update_time':self.current_time}, commit=True)

        set_user_session(user, utb)

        return True
