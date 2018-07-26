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
from xml2json import xml2json
try:
    from urllib.parse import urlencode
except ImportError as identifier:
    from urllib import urlencode

from flask_babel import gettext as _
from flask import (
    session,
    request,
    redirect
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


class JsapiOpenidService(object):
    """jsapi获取openidService"""

    def __init__(self, redirect_url):
        self.msg           = u''
        self.redirect_url  = redirect_url
        self.current_time  = current_timestamp()
        self.code_url      = ''
        self.appid         = ''
        self.secret        = ''
        self.code          = ''
        self.openid        = ''
        self.opentime      = ''

    def _code_url(self):
        """创建获取code的uri"""

        weixin_authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        redirect_uri         = url_push_query(request.url, 'redirect_url=%s' % self.redirect_url)
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

        url         = u'%s?%s' % (access_token_url, urlencode(params))
        res         = requests.get(url)
        jsonobj     = res.json()
        self.openid = jsonobj['openid']

    def check(self):
        """检查"""

        ss = SysSetting.query.filter(SysSetting.key == 'config_paymethod_weixinjsapi').first()
        if not ss:
            self.msg = _(u'配置错误')
            return False

        try:
            config_paymethod_weixinjsapi = json.loads(ss.value)
        except Exception as e:
            self.msg = _(u'配置错误')
            return False

        self.appid  = config_paymethod_weixinjsapi.get('appid', '')
        self.secret = config_paymethod_weixinjsapi.get('secret', '')

        if self.appid == '' or self.secret == '':
            self.msg = _(u'配置错误')
            return False

        return True

    def set_openid(self):
        """设置openid"""

        self.code          = request.args.get('code', '')
        self.openid        = session.get('jsapi_weixin_openid', '')
        self.opentime      = session.get('jsapi_weixin_opentime', 0)
        is_expire_opentime = self.opentime < (self.current_time-30*60)

        # 跳转到微信获取code
        if not self.code and (not self.openid or is_expire_opentime):
            # 创建获取code的url
            self._code_url()

            return redirect(self.code_url)

        # 根据微信code获取openid
        if self.code and (not self.openid or is_expire_opentime):
            self._get_openid()

            session['jsapi_weixin_openid']   = self.openid
            session['jsapi_weixin_opentime'] = self.current_time

            redirect_url = request.args.get('redirect_url')
            return redirect(redirect_url)

        return True


class JsapiPayParamsService():
    """jsapi支付参数Service"""

    def __init__(self, tran_id, openid, body, total_fee, nonce_str, spbill_create_ip=''):
        """
        @param tran_id:             交易ID
        @param openid:              openid
        @param body:                订单信息
        @param total_fee:           订单金额
        @param nonce_str:           32位内随机字符串
        @param spbill_create_ip:    客户端请求IP地址
        """
        self.msg              = u''
        self.tran_id          = tran_id
        self.openid           = openid
        self.body             = body
        self.total_fee        = total_fee
        self.nonce_str        = nonce_str
        self.spbill_create_ip = spbill_create_ip
        self.current_time     = current_timestamp()
        self.appid            = ''
        self.secret           = ''
        self.mch_id           = ''
        self.partner_key      = ''
        self.notify_url       = ''
        self.prepay_id        = ''
        self.sign_params      = {}
        self.pay_params       = {}

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
        """创建签名"""

        url_str  = self._key_value_to_url_str(params)
        sign_str = '%s&key=%s' % (url_str, self.partner_key)

        return (md5(sign_str).hexdigest()).upper()

    def _get_prepay_xml(self):
        """拼接XML"""

        self.sign_params['sign'] = self._create_sign(self.sign_params)

        xml = "<xml>"
        for k, v in self.sign_params.items():
            v = v.encode('utf8')
            k = k.encode('utf8')
            xml += '<' + k + '>' + v + '</' + k + '>'
        xml += "</xml>"

        return xml

    def _set_prepay_id(self):
        """设置获取prepay_id"""

        url     = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        xml     = self._get_prepay_xml()
        headers = {'Content-Type': 'application/xml'}

        # 请求
        respone    = requests.post(url, data=xml, headers=headers)
        re_xml     = ElementTree.fromstring(respone.text.encode('utf8'))
        xml_status = re_xml.getiterator('result_code')[0].text

        if xml_status != 'SUCCESS':
            self.msg = _(u"连接微信出错啦！")
            return False

        self.prepay_id = re_xml.getiterator('prepay_id')[0].text

        return True

    def _set_sign_params(self):
        """设置创建签名参数"""

        self.spbill_create_ip = self.spbill_create_ip if self.spbill_create_ip else '114.114.114.114'

        self.sign_params = {
            'appid':self.appid,
            'mch_id':self.mch_id,
            'nonce_str':self.nonce_str,
            'body':self.body,
            'out_trade_no':str(self.tran_id),
            'total_fee':str(int(self.total_fee)),
            'spbill_create_ip':self.spbill_create_ip,
            'trade_type':'JSAPI',
            'notify_url':self.notify_url,
            'openid':self.openid
        }

        return True

    def _set_pay_params(self):
        """设置支付签名参数"""

        self.pay_params = {
            'appId':self.appid,
            'timeStamp':str(self.current_time),
            'nonceStr':self.nonce_str,
            'package':'prepay_id=%s' % self.prepay_id,
            'signType':'MD5'
        }

        self.pay_params['paySign'] = self._create_sign(self.pay_params)

        return True

    def check(self):
        """检查"""

        ss = SysSetting.query.filter(SysSetting.key == 'config_paymethod_weixinjsapi').first()
        if not ss:
            self.msg = _(u'配置错误')
            return False

        try:
            config_paymethod_weixinjsapi = json.loads(ss.value)
        except Exception as e:
            self.msg = _(u'配置错误')
            return False

        self.appid       = config_paymethod_weixinjsapi.get('appid', '')
        self.secret      = config_paymethod_weixinjsapi.get('secret', '')
        self.mch_id      = config_paymethod_weixinjsapi.get('mch_id', '')
        self.partner_key = config_paymethod_weixinjsapi.get('partner_key', '')
        self.notify_url  = config_paymethod_weixinjsapi.get('notify_url', '')

        if self.appid == '' or self.secret == '' or self.mch_id == '' or self.partner_key == '' or self.notify_url == '':
            self.msg = _(u'配置错误')
            return False

        self._set_sign_params()

        if not self._set_prepay_id():
            self.msg = _(u'设置prepayId出错')
            return False

        return True

    def create(self):
        """创建支付参数"""

        self._set_pay_params()

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

        repone_xml   = ElementTree.fromstring(self.xml)
        return_code  = repone_xml.getiterator('result_code')[0].text
        err_code     = repone_xml.getiterator('err_code')[0].text
        err_code_des = repone_xml.getiterator('err_code_des')[0].text
        if return_code != 'SUCCESS':
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][ResponeError]  xml:%s code:%s des:%s' %\
                        (self.xml, err_code, err_code_des))
            return False

        ss = SysSetting.query.filter(SysSetting.key == 'config_paymethod_weixinjsapi').first()
        if not ss:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][SettingError01]  xml:%s ' % self.xml)
            return False

        try:
            config_paymethod_weixinjsapi = json.loads(ss.value)
        except Exception as e:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][SettingError02]  xml:%s ' % self.xml)
            return False

        self.partner_key = config_paymethod_weixinjsapi.get('partner_key', '')

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
        params   = json.loads(xml2json(self.xml, options))['xml']
        _sign    = params.get('sign', '')

        params.pop('sign')
        sign = self._create_sign(params)

        # 验证签名
        if _sign != sign:
            log_error('[ErrorServiceApiPayWeixinJsapiNotifyServiceVerify][VerifyError]  xml:%s ' % self.xml)
            return False

        return True
