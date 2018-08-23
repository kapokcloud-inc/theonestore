# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import requests
try:
    from urllib.parse import urlencode
except ImportError as identifier:
    from urllib import urlencode

from flask_babel import gettext as _
from flask import (
    request,
    url_for
)

from app.helpers import (
    log_info,
    log_error,
    toint,
    toamount,
    model_create,
    model_update
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str
)

from app.models.sys import (
    SysSetting,
    SysToken
)
from app.models.order import (
    Order,
    OrderGoods
)
from app.models.user import (
    User,
    UserThirdBind
)
from app.models.weixin import WeixinMpTemplate


class WeiXinMpAccessTokenService(object):
    """微信公众平台AccessTokenService"""

    def __init__(self):
        self.appid        = ''
        self.secret       = ''
        self.current_time = current_timestamp()
        self.st           = None

    def __check(self):
        """检查"""

        ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_mp').first()
        if not ss:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config is none.')
            return False

        try:
            config = json.loads(ss.value)
        except Exception as e:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config data error.')
            return False

        self.appid  = config.get('appid', '')
        self.secret = config.get('secret', '')
        if (not self.appid) or (not self.secret):
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceCheck][ConfigError]  config is empty.')
            return False

        return True

    def __request_token(self):
        """获取token"""

        token = ''

        if not self.__check():
            return token

        
        params = {'grant_type':'client_credential',
                    'appid':self.appid.encode('utf8'),
                    'secret':self.secret.encode('utf8')}
        url    = 'https://api.weixin.qq.com/cgi-bin/token'
        url    = u'%s?%s' % (url, urlencode(params))

        response = requests.get(url)
        if response.status_code != 200:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceRequestToken][RequestError]  request error.')
            return token

        data    = response.json()
        errcode = data.get('errcode', 0)
        errmsg  = data.get('errmsg', '')
        if errcode > 0:
            log_error('[ErrorServiceWeixinWeiXinMpAccessTokenServiceRequestToken][RequestError]  errcode:%s  errmsg:%s' %\
                (errcode, errmsg))
            return token

        token      = data.get('access_token', '')
        expires_in = data.get('expires_in', 0)

        if not self.st:
            self.st = model_create(SysToken, {'token_type':'weixin_mp', 'add_time':self.current_time})

        expires_in = self.current_time + expires_in - 60
        model_update(self.st, {'access_token':token, 'expires_in':expires_in}, commit=True)

        return token

    def get_token(self):
        """获取token"""
        token   = ''
        expires = 0

        self.st = SysToken.query.filter(SysToken.token_type == 'weixin_mp').first()
        if self.st:
            token   = self.st.access_token
            expires = self.st.expires_in

        if (token == '') or (self.current_time > expires):
            token = self.__request_token()

        return token


class WeiXinMpMessageService(object):
    """微信公众平台模板消息Service"""

    def __init__(self, uid, wmt_id, data, url=''):
        self.uid          = uid
        self.wmt_id       = wmt_id
        self.data         = data
        self.url          = url
        self.current_time = current_timestamp()
        self.openid       = ''
        self.access_token = ''
        self.template_id  = ''

    def __check(self):
        """检查"""

        utb = UserThirdBind.query.filter(UserThirdBind.uid == self.uid).first()
        if not utb or utb.third_user_id == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][UserError]  no openid.')
            return False
        self.openid = utb.third_user_id

        wmats             = WeiXinMpAccessTokenService()
        self.access_token = wmats.get_token()
        if self.access_token == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][AccessTokenError]  no token.')
            return False

        wmt = WeixinMpTemplate.query.get(self.wmt_id)
        if not wmt or wmt.template_id == '':
            log_error('[ErrorServiceWeixinWeiXinMpMessageServiceCheck][TemplateError]  no template.')
            return False
        self.template_id = wmt.template_id

        return True

    def push(self):
        """推送"""
        if not self.__check():
            return False

        url  = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % self.access_token
        data = {'touser':self.openid, 'template_id':self.template_id, 'data':self.data, 'url':self.url}
        data = json.dumps(data)
        response = requests.post(url, data=data)
        if response.status_code != 200:
            log_error('[ErrorServiceWeixinWeiXinMpMessageServicePush][RequestError]  request error.')
            return False

        data    = response.json()
        errcode = data.get('errcode', 0)
        errmsg  = data.get('errmsg', '')
        if errcode > 0:
            log_error('[ErrorServiceWeixinWeiXinMpMessageServicePush][RequestError]  errcode:%s  errmsg:%s' %\
                (errcode, errmsg))
            return False

        return True


class WeixinMessageStaticMethodsService(object):

    @staticmethod
    def create_order(order):
        """推送创建订单消息"""

        pay_amount = _(u'%s元' % toamount(order.pay_amount).__str__())

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.order.detail', order_id=order.order_id))
        data = {'first':{'color':'#000000', 'value':_(u'您的订单已创建，请尽快完成支付。')},
                'keyword1':{'color':'#000000', 'value':order.order_sn},
                'keyword2':{'color':'#000000', 'value':pay_amount},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情在线付款。')}}

        wxmms = WeiXinMpMessageService(order.uid, 1, data, url)
        wxmms.push()

        return True

    @staticmethod
    def paid(order):
        """推送付款成功消息"""

        paymethods  = {'funds':_(u'钱包支付'), 'weixin':_(u'微信支付')}
        paymethod   = paymethods.get(order.pay_method, '')
        paid_time   = timestamp2str(order.paid_time, 'YYYY-MM-DD HH:mm:ss')
        paid_amount = _(u'%s元' % toamount(order.paid_amount).__str__())

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.order.detail', order_id=order.order_id))
        data = {'first':{'color':'#000000', 'value':_(u'您好，您有一笔订单已经支付成功。')},
                'keyword1':{'color':'#000000', 'value':order.order_sn},
                'keyword2':{'color':'#000000', 'value':paid_time},
                'keyword3':{'color':'#000000', 'value':paid_amount},
                'keyword4':{'color':'#000000', 'value':paymethod},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看订单。')}}

        wxmms = WeiXinMpMessageService(order.uid, 2, data, url)
        wxmms.push()

        return True

    @staticmethod
    def shipping(order):
        """推送发货消息"""

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.order.detail', order_id=order.order_id))
        data = {'first':{'color':'#000000', 'value':_(u'亲，宝贝已经启程了，好想快点来到你身边。')},
                'keyword1':{'color':'#000000', 'value':order.order_sn},
                'keyword2':{'color':'#000000', 'value':order.shipping_name},
                'keyword3':{'color':'#000000', 'value':order.shipping_sn},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看订单。')}}

        wxmms = WeiXinMpMessageService(order.uid, 3, data, url)
        wxmms.push()

        return True

    @staticmethod
    def deliver(order):
        """推送收货消息"""

        add_time      = timestamp2str(order.add_time, 'YYYY-MM-DD HH:mm:ss')
        shipping_time = timestamp2str(order.shipping_time, 'YYYY-MM-DD HH:mm:ss')
        deliver_time  = timestamp2str(order.deliver_time, 'YYYY-MM-DD HH:mm:ss')

        items  = []
        _items = db.session.query(OrderGoods.goods_name).\
                            filter(OrderGoods.order_id == order.order_id).all()
        for _item in _items:
            items.append('[%s]' % _item.goods_name)
        items = ','.join(items)

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.order.detail', order_id=order.order_id))
        data = {'first':{'color':'#000000', 'value':_(u'亲：您在我们商城买的宝贝已经确认收货。')},
                'keyword1':{'color':'#000000', 'value':order.order_sn},
                'keyword2':{'color':'#000000', 'value':items},
                'keyword3':{'color':'#000000', 'value':add_time},
                'keyword4':{'color':'#000000', 'value':shipping_time},
                'keyword5':{'color':'#000000', 'value':deliver_time},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看订单。')}}

        wxmms = WeiXinMpMessageService(order.uid, 4, data, url)
        wxmms.push()

        return True

    @staticmethod
    def refund(refund):
        """推送退款消息"""

        order          = Order.query.get(refund.order_id)
        refunds_amount = _(u'%s元' % toamount(refund.refunds_amount).__str__())

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.order.detail', order_id=order.order_id))
        data = {'first':{'color':'#000000', 'value':_(u'退款成功。')},
                'reason':{'color':'#000000', 'value':refund.remark_user},
                'refund':{'color':'#000000', 'value':refunds_amount},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看退款详情。')}}

        wxmms = WeiXinMpMessageService(order.uid, 5, data, url)
        wxmms.push()

        return True

    @staticmethod
    def recharge(order):
        """推送充值消息"""

        goods_amount = _(u'%s元' % toamount(order.goods_amount).__str__())
        user         = User.query.get(order.uid)

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.wallet.root'))
        data = {'first':{'color':'#000000', 'value':_(u'您好，您已成功进行会员帐号充值。')},
                'accountType':{'color':'#000000', 'value':_(u'会员帐号')},
                'account':{'color':'#000000', 'value':user.nickname},
                'amount':{'color':'#000000', 'value':goods_amount},
                'result':{'color':'#000000', 'value':_(u'充值成功')},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看充值详情。')}}

        wxmms = WeiXinMpMessageService(order.uid, 6, data, url)
        wxmms.push()

        return True

    @staticmethod
    def aftersale_step(aftersale, status, content):
        """推送售后处理进度消息"""

        aftersales_types = {1:_(u'仅退款'), 2:_(u'退货退款'), 3:_(u'仅换货')}
        aftersales_type  = aftersales_types.get(aftersale.aftersales_type)
        first            = _(u'您好，您的售后单%s有新的客服回复' % aftersale.aftersales_sn)
        current_time     = timestamp2str(current_timestamp(), 'YYYY-MM-DD HH:mm:ss')

        url  = '%s%s' % (request.host_url.strip('/'), url_for('mobile.aftersales.detail', aftersales_id=aftersale.aftersales_id))
        data = {'first':{'color':'#000000', 'value':first},
                'HandleType':{'color':'#000000', 'value':aftersales_type},
                'Status':{'color':'#000000', 'value':status},
                'RowCreateDate':{'color':'#000000', 'value':current_time},
                'LogType':{'color':'#000000', 'value':content},
                'remark':{'color':'#000000', 'value':_(u'感谢您的支持与厚爱，请点击详情查看详细处理结果。')}}

        wxmms = WeiXinMpMessageService(aftersale.uid, 7, data, url)
        wxmms.push()

        return True
