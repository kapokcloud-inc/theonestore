# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import os
import requests
import json
from xml.etree import ElementTree
from hashlib import md5

from flask_babel import gettext as _

from app.helpers import (
    log_debug,
    log_info,
    randomstr
)

from app.models.sys import SysSetting


class JsapiWeixinRefundsService(object):
    """weixin退款service"""

    def __init__(self, pay_tran_id, refund):
        self.msg         = u''
        self.pay_tran_id = pay_tran_id
        self.refund      = refund
        self.refund_url  = 'https://api.mch.weixin.qq.com/secapi/pay/refund' # 退款url
        self.partner_key = u''
        self.cert_file   = u''
        self.key_file    = u''
        self.params      = {}
        self.refund_id   = u''
    
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
        
        appid            = config_paymethod_weixinjsapi.get('appid', '')
        mch_id           = config_paymethod_weixinjsapi.get('mch_id', '')
        self.partner_key = config_paymethod_weixinjsapi.get('partner_key', '')

        if appid == '' or mch_id == '' or self.partner_key == '':
            self.msg = _(u'配置错误')
            return False

        self.cert_file = os.path.join(os.getcwd(), 'cert', 'weixin', 'apiclient_cert.pem')
        self.key_file  = os.path.join(os.getcwd(), 'cert', 'weixin', 'apiclient_key.pem')
        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            self.msg = _(u'证书文件不存在')
            return False

        self.params = {
            'appid':appid,
            'mch_id':mch_id,
            'nonce_str':randomstr(32),
            'op_user_id':mch_id,
            'out_refund_no':self.refund.refund_id,
            'out_trade_no':self.refund.tran_id,
            'refund_fee':int(self.refund.refund_amount*100),
            'total_fee':int(self.refund.refund_amount*100),
            'transaction_id':self.pay_tran_id,
        }

        return True

    def refunds(self):
        """退款"""

        # 创建签名
        key  = self.partner_key
        keys = self.params.keys()
        keys.sort()

        # 创建签名
        signstr = u''
        for k in keys:
            val = self.params[k]
            if val:
                signstr += u'%s=%s&' % (k, val)
        signstr += 'key=' + key

        # 创建签名
        sign = md5(signstr).hexdigest()
        sign = sign.upper()

        # 更新params
        self.params['sign'] = sign

        # xml
        xml = u'<xml>'
        for k,v in self.params.items():
            xml += u'<%s>%s</%s>' % (k,v,k)
        xml += u'</xml>'

        # 请求退款
        res = requests.post(self.refund_url, data=xml, verify=True, cert=(self.cert_file, self.key_file))

        # 退款结果
        doc = ElementTree.fromstring(res.content)
        return_code    = doc.findtext('return_code')
        return_msg     = doc.findtext('return_msg')
        result_code    = doc.findtext('result_code')
        err_code       = doc.findtext('err_code')
        err_code_des   = doc.findtext('err_code_des')
        self.refund_id = doc.findtext('refund_id')

        if return_code != 'SUCCESS':
            self.msg = return_msg
            return False

        if result_code == 'SUCCESS':
            self.msg = _(u'错误代码：%s  错误代码描述：%s' % (err_code, err_code_des))
            return False

        return True
