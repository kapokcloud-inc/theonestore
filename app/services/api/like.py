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
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import get_uid, get_nickname, get_avatar

from app.models.item import Goods
from app.models.like import Like


class LikeService(object):
    """赞Service"""

    def __init__(self, like_type, ttype, tid, current_time=0):
        self.msg          = u''
        self.like_type    = toint(like_type)    # LIKE类型: 0.默认; 1.点赞; 2.收藏; 3.关注;
        self.ttype        = toint(ttype)        # 第三方类型: 0.默认; 1.商品;
        self.tid          = toint(tid)          # 第三方ID
        self.tname        = u''                 # 第三方名称
        self.timg         = u''                 # 第三方封面图
        self.uid          = get_uid()           # 用户UID
        self.nickname     = get_nickname()      # 用户昵称
        self.avatar       = get_avatar()        # 用户头像
        self.action_code  = 0                   # 0.默认; 1.添加; 2.取消;
        self.ext_data     = '{}'                # 扩展数据, json
        self.like         = None                # Like实例
        self.third_obj    = None                # 第三方实例
        self.current_time = current_time if current_time else current_timestamp()

    def commit(self):
        """提交sql事务"""

        db.session.commit()

    def _check_third(self):
        """检查第三方"""

        if self.ttype == 1:
            self.third_obj = Goods.query.get(self.tid)
            if not self.third_obj:
                self.msg = _(u'商品不存在')
                return False

            self.tname    = self.third_obj.goods_name
            self.timg     = self.third_obj.goods_img
            self.ext_data = json.dumps({'goods_desc':self.third_obj.goods_desc})
        else:
            self.msg = _(u'第三方类型错误')
            return False

        return True

    def _update_third(self):
        """更新第三方冗余数据"""

        # 点赞
        if self.like_type == 1:
            # 点赞总数
            like_count = self.third_obj.like_count + 1 if self.action_code == 1 else self.third_obj.like_count - 1

            self.third_obj.like_count = like_count

        # 收藏
        if self.like_type == 2:
            # 收藏总数
            fav_count = self.third_obj.fav_count + 1 if self.action_code == 1 else self.third_obj.fav_count - 1

            self.third_obj.fav_count = fav_count

        # 关注
        if self.like_type == 3:
            # 粉丝总数
            fans_count = self.third_obj.fans_count + 1 if self.action_code == 1 else self.third_obj.fans_count - 1

            self.third_obj.fans_count = fans_count

        return True

    def check(self):
        """检查"""

        # 检查
        if self.like_type not in [1,2,3]:
            self.msg = _(u'LIKE类别错误')
            return False

        # 检查
        if not self.uid:
            self.msg = _(u'用户信息错误')
            return False

        # 检查
        if not self._check_third():
            return False

        self.like = Like.query.filter(Like.like_type == self.like_type).\
                            filter(Like.uid == self.uid).\
                            filter(Like.ttype == self.ttype).\
                            filter(Like.tid == self.tid).first()

        return True

    def action(self):
        """操作:点赞或取消"""

        if self.like:
            self.action_code = 2
            db.session.delete(self.like)
        else:
            self.action_code = 1
            self.like = Like()
            self.like.like_type = self.like_type
            self.like.uid = self.uid
            self.like.nickname = self.nickname
            self.like.avatar = self.avatar
            self.like.ttype = self.ttype
            self.like.tid = self.tid
            self.like.tname = self.tname
            self.like.timg = self.timg
            self.like.ext_data = self.ext_data
            self.like.add_time = self.current_time
            db.session.add(self.like)

        # 更新第三方冗余数据
        self._update_third()

        return True

    def get_like_list(self, p, ps):
        """获取赞列表"""

        like_list = db.session.query(Like.like_id, Like.uid, Like.nickname, Like.avatar, Like.signature, Like.add_time).\
                            filter(Like.like_type == self.like_type).\
                            filter(Like.ttype == self.ttype).\
                            filter(Like.tid == self.tid).\
                            order_by(Like.like_id.desc()).limit(ps).offset((p-1) * ps).all()

        return like_list


class LikeStaticMethodsService(object):
    """赞静态方法Service"""

    @staticmethod
    def likes(params, is_pagination=False):
        """获取赞列表"""

        p   = toint(params.get('p', '1'))
        ps  = toint(params.get('ps', '10'))
        uid = toint(params.get('uid', '0'))

        q     = db.session.query(Like.like_id, Like.like_type, Like.ttype, Like.tid, Like.tname, Like.timg,
                                    Like.ext_data, Like.add_time).\
                    filter(Like.uid == uid).\
                    filter(Like.like_type == 2).\
                    filter(Like.ttype == 1)
        likes = q.order_by(Like.like_id.desc()).offset((p-1)*ps).limit(ps).all()

        pagination = None
        if is_pagination:
            pagination = Pagination(None, p, ps, q.count(), None)

        return {'likes':likes, 'pagination':pagination}
