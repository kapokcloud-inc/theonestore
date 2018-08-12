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
from flask_sqlalchemy import Pagination
from app.database import db

from app.helpers import (
    log_info,
    toint,
    model_to_dict,
    model_create
)
from app.helpers.date_time import (
    current_timestamp,
    some_day_timestamp
)

from app.models.user import User
from app.models.message import Message


class MessageCreateService(object):
    """创建消息Service"""

    # message_type: 消息类型
        ## 0.默认; 1.系统通知;

    # tuid: 接收用户ID
        ## 0.所有用户;
    
    # fuid: 来源用户ID
        ## -1.系统; 0.接收用户自己; >0:其它用户ID;
    
    # ttype: 第三方类型
        ## 0.默认; 1.订单; 2.订单商品;

    # tid: 第三方ID
        ##

    def __init__(self, message_type, tuid, fuid=0, content=u'', img=u'', ttype=0, tid=0, data={}, current_time=0):
        self.msg               = u''
        self.message_type      = message_type
        self.tuid              = tuid
        self.fuid              = fuid
        self.content           = content
        self.img               = img
        self.ttype             = toint(ttype)
        self.tid               = toint(tid)
        self.data              = json.dumps(data) if data else json.dumps('{}')
        self.message_type_list = [1]
        self.ttype_list        = [1]
        self.current_time      = current_time if current_time else current_timestamp()
        self.today_timestamp   = some_day_timestamp(current_time, 0)
        self.message           = None
        self.tuser             = None
        self.fuser             = {'uid':self.fuid}

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def check(self):
        """检查"""

        # 检查 - 接收用户
        self.tuser = User.query.get(self.tuid)
        if not self.tuser:
            self.msg = _(u'用户不存在')
            return False

        # 检查 - 来源用户
        if self.fuid > 0:
            self.fuser = User.query.get(self.fuid)
            if not self.fuser:
                self.msg = _(u'用户不存在')
                return False

            self.fuser = model_to_dict(self.fuser)

        # 检查 - 动态类型
        if self.message_type not in self.message_type_list:
            self.msg = _(u'通知类型错误')
            return False

        # 检查 - 第三方类型
        if self.ttype not in self.ttype_list:
            self.msg = _(u'第三方类型错误')
            return False

        return True

    def do(self):
        """通知"""

        data = {'message_type':self.message_type, 'content':self.content, 'img':self.img, 'data':self.data,
                'fuid':self.fuser.get('uid', 0), 'fname':self.fuser.get('nickname', ''), 'favatar':self.fuser.get('avatar', ''),
                'tuid':self.tuser.uid, 'tname':self.tuser.nickname, 'tavatar':self.tuser.avatar,
                'tid':self.tid, 'ttype':self.ttype, 'add_time':self.current_time, 'add_date':self.today_timestamp}
        self.message = model_create(Message, data, commit=True)
        
        # 微信推送 ??

        return True


class MessageStaticMethodsService(object):
    """消息静态方法Service"""

    @staticmethod
    def messages(params, is_pagination=False):
        """获取消息列表"""

        p   = toint(params.get('p', '1'))
        ps  = toint(params.get('ps', '10'))
        uid = toint(params.get('uid', '0'))

        q        = db.session.query(Message.message_id, Message.message_type, Message.content,
                                    Message.ttype, Message.tid, Message.add_time).\
                    filter(Message.tuid == uid)
        messages = q.order_by(Message.message_id.desc()).offset((p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        return {'messages':messages, 'pagination':pagination}
