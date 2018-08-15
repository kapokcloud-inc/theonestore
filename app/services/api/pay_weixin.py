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
import optparse
from decimal import Decimal
from hashlib import md5
from xml.etree import ElementTree
try:
    from urllib.parse import urlencode
except ImportError as identifier:
    from urllib import urlencode

from flask_babel import gettext as _
from flask import (
    session,
    request,
    url_for
)

from app.database import db

from app.helpers import (
    log_error,
    log_info,
    toint,
    url_push_query
)
from app.helpers.date_time import current_timestamp
from app.models.sys import SysSetting
from app.ext.xml2json import xml2json


class UnifiedorderService(object):
    """统一下单Service"""

    def __init__(self, nonce_str, body, out_trade_no, total_fee, trade_type,
                spbill_create_ip='', openid=''):
        """
        @param nonce_str:           32位内随机字符串
        @param body:                订单信息
        @param out_trade_no:        商户订单号(交易ID)
        @param total_fee:           交易金额
        @param trade_type:          交易类型，JSAPI(公众号支付)、NATIVE(扫码支付)、APP(APP支付)
        @param spbill_create_ip:    客户端请求IP地址
        @param openid:              用户标识，trade_type=JSAPI时（即公众号支付），此参数必传，此参数为微信用户在商户对应appid下的唯一标识。
        """
        self.msg              = u''
        self.nonce_str        = nonce_str
        self.body             = body
        self.out_trade_no     = out_trade_no
        self.total_fee        = total_fee
        self.trade_type       = trade_type
        self.spbill_create_ip = spbill_create_ip
        self.openid           = openid
        self.current_time     = current_timestamp()
        self.appid            = ''
        self.secret           = ''
        self.mch_id           = ''
        self.partner_key      = ''
        self.notify_url       = '%s%s' % (request.host_url.strip('/'), url_for('api.pay.notify'))
        self.prepay_id        = ''
        self.code_url         = ''
        self.sign_params      = {}

    def __key_value_to_url_str(self, params):
        """将键值对转为:key1=value1&key2=value2"""

        pairs = []
        keys  = sorted(params.keys())

        for k in keys:
            v = params.get(k, '').strip()
            v = v.encode('utf8')
            k = k.encode('utf8')
            pairs.append('%s=%s' % (k, v))

        _str = '&'.join(pairs)

        return _str

    def __create_sign(self, params):
        """创建签名"""

        url_str  = self.__key_value_to_url_str(params)
        sign_str = '%s&key=%s' % (url_str, self.partner_key)

        return (md5(sign_str).hexdigest()).upper()

    def __get_prepay_xml(self):
        """拼接XML"""

        self.sign_params['sign'] = self.__create_sign(self.sign_params)

        xml = "<xml>"
        for k, v in self.sign_params.items():
            v = v.encode('utf8')
            k = k.encode('utf8')
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"

        return xml

    def __check(self):
        """检查"""

        if self.trade_type == 'JSAPI' and not self.openid:
            self.msg = _(u'缺少openid')
            return False

        # 检查 - 配置
        cpw_ss = SysSetting.query.filter(SysSetting.key == 'config_paymethod_weixin').first()
        cwm_ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_mp').first()
        if not cpw_ss or not cwm_ss:
            self.msg = _(u'配置错误')
            return False

        # 检查 - 配置
        try:
            config_paymethod_weixin = json.loads(cpw_ss.value)
            config_weixin_mp        = json.loads(cwm_ss.value)
        except Exception as e:
            self.msg = _(u'配置错误')
            return False

        # 检查 - 配置
        self.appid       = config_weixin_mp.get('appid', '').encode('utf8')
        self.secret      = config_weixin_mp.get('secret', '').encode('utf8')
        self.mch_id      = config_paymethod_weixin.get('mch_id', '').encode('utf8')
        self.partner_key = config_paymethod_weixin.get('partner_key', '').encode('utf8')
        if self.appid == '' or self.secret == '' or self.mch_id == '' or self.partner_key == '':
            self.msg = _(u'配置错误')
            return False

        return True

    def __set_sign_params(self):
        """设置创建签名参数"""

        self.spbill_create_ip = self.spbill_create_ip if self.spbill_create_ip else '114.114.114.114'

        self.sign_params = {
            'appid':self.appid,
            'mch_id':self.mch_id,
            'nonce_str':self.nonce_str,
            'body':self.body,
            'out_trade_no':str(self.out_trade_no),
            'total_fee':str(int(self.total_fee)),
            'spbill_create_ip':self.spbill_create_ip,
            'trade_type':self.trade_type,
            'notify_url':self.notify_url
        }

        if self.trade_type == 'JSAPI':
            self.sign_params['openid'] = self.openid

    def unifiedorder(self):
        """统一下单"""

        # 检查
        if not self.__check():
            return False

        # 设置创建签名参数
        self.__set_sign_params()

        # 请求下单
        url     = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        xml     = self.__get_prepay_xml()
        headers = {'Content-Type': 'application/xml'}
        respone = requests.post(url, data=xml, headers=headers)

        # 下单结果
        doc            = ElementTree.fromstring(respone.content)
        return_code    = doc.findtext('return_code')
        return_msg     = doc.findtext('return_msg')
        result_code    = doc.findtext('result_code')
        err_code       = doc.findtext('err_code')
        err_code_des   = doc.findtext('err_code_des')
        self.prepay_id = doc.findtext('prepay_id')
        self.code_url  = doc.findtext('code_url')

        # 下单结果
        if return_code != 'SUCCESS':
            self.msg = return_msg
            return False

        # 下单结果
        if result_code != 'SUCCESS':
            self.msg = _(u'错误代码：%s  错误代码描述：%s' % (err_code, err_code_des))
            return False

        return True

    def get_jsapi_pay_params(self):
        """获取JSAPI支付签名参数"""

        pay_params = {
            'appId':self.appid,
            'timeStamp':str(self.current_time),
            'nonceStr':self.nonce_str,
            'package':'prepay_id=%s' % self.prepay_id,
            'signType':'MD5'
        }

        pay_params['paySign'] = self.__create_sign(pay_params)

        return pay_params


class JsapiOpenidService(object):
    """jsapi获取openidService"""

    def __init__(self):
        self.msg           = u''
        self.current_time  = current_timestamp()
        self.order_id      = 0
        self.code_url      = ''
        self.redirect_url  = ''
        self.appid         = ''
        self.secret        = ''
        self.code          = ''
        self.openid        = ''
        self.opentime      = ''

    def _code_url(self):
        """创建获取code的uri"""

        weixin_authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        redirect_uri         = url_push_query(request.url, 'order_id=%s' % self.order_id)
        params               = {'redirect_uri':redirect_uri.encode('utf8')}
        redirect_uri_param   = urlencode(params)
        self.code_url        = u'%s?appid=%s&%s&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect' % (
                                    weixin_authorize_url, self.appid, redirect_uri_param)

        return True

    def _get_openid(self):
        """获取openid"""

        access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params           = {'appid':self.appid.encode('utf8'), 'secret':self.secret.encode('utf8'),
                            'code':self.code.encode('utf8'), 'grant_type':'authorization_code'.encode('utf8')}

        url     = u'%s?%s' % (access_token_url, urlencode(params))
        res     = requests.get(url)
        jsonobj = res.json()

        session['jsapi_weixin_openid']   = jsonobj['openid']
        session['jsapi_weixin_opentime'] = self.current_time

    def check(self):
        """检查"""

        cwm_ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_mp').first()
        if not cwm_ss:
            self.msg = _(u'配置错误')
            return False

        try:
            config_weixin_mp = json.loads(cwm_ss.value)
        except Exception as e:
            self.msg = _(u'配置错误')
            return False

        self.appid  = config_weixin_mp.get('appid', '')
        self.secret = config_weixin_mp.get('secret', '')

        if self.appid == '' or self.secret == '':
            self.msg = _(u'配置错误')
            return False

        return True

    def set_openid(self):
        """设置openid"""

        self.code          = request.args.get('code', '').strip()
        self.order_id      = toint(request.args.get('order_id', '0'))
        self.openid        = session.get('jsapi_weixin_openid', '')
        self.opentime      = session.get('jsapi_weixin_opentime', 0)
        is_expire_opentime = self.opentime < (self.current_time-30*60)

        # 跳转到微信获取code
        if not self.code and (not self.openid or is_expire_opentime):
            # 创建获取code的url
            self._code_url()
            return True

        # 根据微信code获取openid
        if self.code and (not self.openid or is_expire_opentime):
            # 获取openid
            self._get_openid()

            self.redirect_url = url_for('mobile.cart.checkout', order_id=self.order_id)
            return True
        
        self.code_url = url_for('mobile.cart.checkout', order_id=self.order_id)
        return True


class JsapiNotifyService():
    """jsapi回调Service"""

    def __init__(self, xml):
        self.xml            = xml
        self.partner_key    = ''
        self.transaction_id = ''
        self.out_trade_no   = 0
        self.total_fee      = 0

    def _key_value_to_url_str(self, params):
        """将键值对转为:key1=value1&key2=value2"""

        pairs = []
        keys  = sorted(params.keys())

        for k in keys:
            v = params.get(k, '').strip()
            v = v.encode('utf8')
            k = k.encode('utf8')
            pairs.append('%s=%s' % (k, v))

        _str = '&'.join(pairs)

        return _str

    def _create_sign(self, params):
        """设置签名"""

        url_str  = self._key_value_to_url_str(params)
        sign_str = '%s&key=%s' % (url_str, self.partner_key)

        return (md5(sign_str).hexdigest()).upper()

    def check(self):
        """检查"""

        repone_xml  = ElementTree.fromstring(self.xml)
        return_code = repone_xml.getiterator('result_code')[0].text
        if return_code != 'SUCCESS':
            err_code     = repone_xml.getiterator('err_code')[0].text
            err_code_des = repone_xml.getiterator('err_code_des')[0].text

            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][ResponeError]  xml:%s code:%s des:%s' %\
                        (self.xml, err_code, err_code_des))
            return False

        cpw_ss = SysSetting.query.filter(SysSetting.key == 'config_paymethod_weixin').first()
        if not cpw_ss:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][SettingError01]  xml:%s ' % self.xml)
            return False

        try:
            config_paymethod_weixin = json.loads(cpw_ss.value)
        except Exception as e:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][SettingError02]  xml:%s ' % self.xml)
            return False

        self.partner_key = config_paymethod_weixin.get('partner_key', '')

        if self.partner_key == '':
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][SettingError03]  xml:%s ' % self.xml)
            return False

        self.transaction_id = repone_xml.getiterator('transaction_id')[0].text
        self.out_trade_no   = toint(repone_xml.getiterator('out_trade_no')[0].text)
        self.total_fee      = Decimal(repone_xml.getiterator('total_fee')[0].text)

        return True

    def verify(self):
        """验证签名"""

        options  = optparse.Values({"pretty":False})
        params   = json.loads(xml2json(self.xml))['xml']
        _sign    = params.get('sign', '')

        params.pop('sign')
        sign = self._create_sign(params)

        # 验证签名
        if _sign != sign:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][VerifyError]  xml:%s ' % self.xml)
            return False

        return True
