# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import datetime
import json
import types
import time
from decimal import Decimal

from flask import current_app
from flask_babel import gettext as _
from sqlalchemy.util import KeyedTuple

from app.database import db


def to_json(ret=0, msg='ok', data=None):
    now = int(time.time())
    jsondata = {'ret':ret, 'msg':msg, 'timestamp':now}

    if not data:
        return json.dumps(jsondata)

    jsondata['data'] = data
    return json_encode(jsondata)


def json_encode(data):
    def _any(data):
        ret = None
        if isinstance(data, (list, tuple)):
            ret = _list(data)
        elif isinstance(data, dict):
            ret = _dict(data)
        elif isinstance(data, Decimal):
            ret = str(data)
        elif isinstance(data, db.Model):
            ret = _model(data)
        elif isinstance(data, KeyedTuple):
            ret = _dict(data._asdict())
        elif isinstance(data, datetime.datetime):
            ret = _datetime(data)
        elif isinstance(data, datetime.date):
            ret = _date(data)
        elif isinstance(data, datetime.time):
            ret = _time(data)
        else:
            ret = data

        return ret

    def _model(data):
        ret = {}
        for c in data.__table__.columns:
            ret[c.name] = _any(getattr(data, c.name))

        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data): 
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret

    def _datetime(data):
        return data.strftime("%s %s" % ("%Y-%m-%d", "%H:%M:%S"))

    def _date(data):
        return data.strftime("%Y-%m-%d")

    def _time(data):
        return data.strftime("%H:%M:%S")

    ret = _any(data)

    return json.dumps(ret)


class ResponseJson(object):
    def __init__(self):
        """初始化函数"""
        self.module_code = None
        self.action_code = None

        self.SYSTEM_BUSY           = 101001 #服务器开小差中，请稍候重试。
        self.SYSTEM_PAGE_NOT_FOUND = 101002 #页面找不到
        self.NOT_LOGIN             = 101110 #用户未登录或者登录超时
        self.PARAM_ERROR           = 101111 #请求参数错误
        self.MODULE_CODE_NONE      = 101112 #module编码为None
        self.ACTION_CODE_NONE      = 101113 #action编码为None
        self.PAGESIZE_TOO_LARGE    = 101114 #页面记录数太大
        self.G_SERVICE_CODE        = {
            self.SYSTEM_BUSY           : _(u'服务器开小差中，请稍候重试。'),
            self.SYSTEM_PAGE_NOT_FOUND : _(u'页面找不到'),
            self.NOT_LOGIN             : _(u'用户未登录或者登录超时'),
            self.PARAM_ERROR           : _(u'请求参数错误'),
            self.MODULE_CODE_NONE      : _(u'module编码为None'),
            self.ACTION_CODE_NONE      : _(u'action编码为None'),
            self.PAGESIZE_TOO_LARGE    : _(u'页面记录数太大'),
        }

    def print_json(self, ret=0, msg='ok', data=None):
        res = current_app.response_class(mimetype='application/json')

        if ret > 99 and msg is 'ok':
            # 从配置文件中获取错误消息
            msg = self.G_SERVICE_CODE.get(ret)

            if msg is None:
                msg = _(u'未知错误')

            res.data = to_json(ret, msg, data)
            return res

        if self.module_code is None:
            res.data = to_json(self.MODULE_CODE_NONE, self.G_SERVICE_CODE.get(self.MODULE_CODE_NONE))
            return res

        if self.action_code is None:
            res.data = to_json(self.ACTION_CODE_NONE, self.G_SERVICE_CODE.get(self.ACTION_CODE_NONE))
            return res

        if ret == 0:
            res.data = to_json(0, msg, data)
            return res

        ret = "%s%s%s" % (self.module_code, self.action_code, ret)
        ret = int(ret)
        res.data = to_json(ret, msg, data)
        return res
