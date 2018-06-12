# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import time
from hashlib import sha256

from flask_babel import gettext as _

from app.helpers import log_info
from app.helpers.date_time import (
    current_timestamp,
    before_after_timestamp
)
from app.models.order import Order


class OderStaticMethodsService(object):
    """ 订单静态方法Service """

    @staticmethod
    def order_status_text_and_action_code(order):
        """ 获取订单状态和订单指令 """
        status_text = u''   # 待付款 待发货 已发货 已取消 已完成
        action_code = []    # 订单指令列表: 1.发货; 2.取消订单;

        if order.order_status == 1:
            if order.pay_status == 1:
                status_text = _(u'待付款')
                action_code = [2]

                return (status_text, action_code)
            
            if order.pay_status == 2:
                if order.shipping_status == 1:
                    status_text = _(u'待发货')
                    action_code = [1]

                    return (status_text, action_code)

                if order.shipping_status == 2 and order.deliver_status == 1:
                    status_text = _(u'已发货')
                    action_code = []

                    return (status_text, action_code)

        if order.order_status == 2:
            status_text = _(u'已完成')
            action_code = []

            return (status_text, action_code)
        
        if order.order_status == 3:
            status_text = _(u'已取消')
            action_code = []

            return (status_text, action_code)

        return (status_text, action_code)
    
    