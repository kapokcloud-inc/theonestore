# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~

    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import time
import importlib
import requests
from hashlib import sha256, md5
from flask_babel import gettext as _
from app.helpers import log_info
from app.models.sys import SysSetting
from app.models.shipping import Shipping
from app.exception import ShippingException


class TrackServiceFactory(object):
    """物流查询工厂类"""

    @staticmethod
    def get_trackservice():
        vendor = SysSetting.query.filter(
            SysSetting.key == 'shipping_vendor').first()
        if vendor is None:
            raise ShippingException(_(u'快递配置查询不存在'))
        TrackClassService = vendor.value
        mod = importlib.import_module(__name__)
        return getattr(mod, TrackClassService)()


class TrackService(object):
    """ 物流查询 """

    def __init__(self):
        # 快递id
        self.shipping_id = 0

        # 快递单号
        self.shipping_sn = ''

        # config_key
        self.config_key = ''

        # 快递信息
        self.shipping = None

        # 快递服务配置
        self.config = None

        # 快递查询接口url
        self.apiurl = ''

        # 收件人电话
        self.receive_phone = ''

    def _init_(self):
        """加载快递信息"""
        self.shipping = Shipping.query.get(self.shipping_id)
        if self.shipping is None:
            raise ShippingException(_(u'快递id不存在'))

        config = SysSetting.query.filter(
            SysSetting.key == self.config_key).first()
        if config is None:
            raise ShippingException(_(u'快递配置不存在'))
        try:
            self.shipping_config = json.loads(config.value)
        except Exception as e:
            raise ShippingException(e)

    def _get_track_response(self):
        """获取跟踪数据"""
        try:
            self._init_()
            self._check_req_params()
            data = self._get_req_params()

        except ShippingException as e:
            raise e

        try:
            res = requests.post(self.apiurl, data, timeout=10)
        except Exception as e:
            log_info('[TrackService] [Error] NetWorkException. %s, %s' % (self.apiurl, data))
            raise ShippingException(_(u'查询失败，网络异常！'))

        res.encoding = 'utf-8'
        if res.status_code != 200:
            raise ShippingException(u'查询失败，网络状态为%d' % res.status_code)
        return res

    def _check_req_params(self):
        """检查请求参数"""
        if self.shipping_sn is None:
            raise ShippingException(_(u'缺少快递单号'))

        # 快递分单则默认查询首个订单号
        _temp_sn_list = self.shipping_sn.split()
        if _temp_sn_list is not None and len(_temp_sn_list) >= 2:
            self.shipping_sn = _temp_sn_list[0]

    def _get_req_params(self):
        """获取请求参数，子类实现"""
        pass

    def track(self, shipping_id, shipping_sn, receive_phone):
        """ 快递查询数据，子类重载 """
        pass


class Shipping100TrackService(TrackService):
    """ 快递100物流查询 """
    def __init__(self):
        TrackService.__init__(self)
        self.config_key = 'config_shipping'
        self.apiurl = 'https://poll.kuaidi100.com/poll/query.do'

    def _get_req_params(self):
        params = {
            'com': self.shipping.shipping_code,
            'num': self.shipping_sn,
        }

        # 拼接字符串后MD5加密,字符串转大写
        conf = self.shipping_config
        json_params = json.dumps(params)
        temp_sign = u'%s%s%s' % (json_params, conf['key'], conf['customer'])
        sign = md5(temp_sign.encode('utf-8')).hexdigest()
        sign = sign.upper()

        # 请求接口参数
        return {
            'customer': conf['customer'],
            'param': json_params,
            'sign': sign
        }

    def track(self, shipping_id, shipping_sn, receive_phone=''):
        """ 查询 """
        self.shipping_id = shipping_id
        self.shipping_sn = shipping_sn
        try:
            res = self._get_track_response()
        except ShippingException as e:
            log_info(u'[Shipping100TrackService] [Error]  shipping_code:%s, shipping_sn:%s, ShippingException:%s' % (self.shipping.shipping_code, self.shipping_sn, e))
            raise e

        resjson = res.json()
        if resjson['message'] != 'ok':
            log_info(u'[Shipping100TrackService] [Error]  shipping_code:%s, shipping_sn:%s, response message:%s' % (self.shipping.shipping_code, self.shipping_sn, resjson['message']))
            raise ShippingException(_(u'查询失败'))

        return resjson['data']


class ShippingAggreateTrackService(TrackService):
    """ 聚合数据物流查询 """
    def __init__(self):
        TrackService.__init__(self)
        self.config_key = 'config_shipping_aggreate'
        self.apiurl = 'http://v.juhe.cn/exp/index'

    def _get_req_params(self):
        # 顺丰需要发件人或收件人手机号后4位
        receiverPhone = ''
        if self.shipping.aggreate_code == 'sf':
            if self.receive_phone is None:
                raise ShippingException(_(u'查询失败，缺少收件人手机号'))

            if len(self.receive_phone) < 11:
                raise ShippingException(_(u'查询失败，收件人手机号错误'))

            receiverPhone = self.receive_phone[-4:]
            log_info(u'[ShippingAggreateTrackService] [info] receiverPhone: %s' % receiverPhone)

        return {
            'com': self.shipping.aggreate_code,
            'no': self.shipping_sn,
            'key': self.shipping_config['key'],
            'dtype': 'json',
            'receiverPhone': receiverPhone,
        }

    def track(self, shipping_id, shipping_sn, receive_phone=''):
        """查询"""
        self.shipping_id = shipping_id
        self.shipping_sn = shipping_sn
        self.receive_phone = receive_phone
        try:
            res = self._get_track_response()
        except ShippingException as e:
            log_info(u'[ShippingAggreateTrackService] [Error]  shipping_code:%s, shipping_sn:%s, ShippingException:%s' % (self.shipping.shipping_code, self.shipping_sn, e))
            raise e

        resjson = res.json()
        if resjson['error_code'] != 0 or not resjson['result']:
            log_info(u'[ShippingAggreateTrackService] [Error]  shipping_code:%s, shipping_sn:%s, response error_code:%s' % (self.shipping.shipping_code, self.shipping_sn, resjson['error_code']))
            raise ShippingException(_(u'查询失败'))

        _track_list = resjson['result']['list']
        track_list = [{
                'time': item['datetime'],
                'ftime': item['datetime'],
                'context': item['remark']
            } for item in _track_list]
        track_list.reverse()
        return track_list
