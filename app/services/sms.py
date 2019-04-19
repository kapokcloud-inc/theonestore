# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import importlib
import json
from datetime import (
    date,
    datetime
)
from app.helpers import (
    log_info,
    log_error,
    urlencode
)

from flask_babel import gettext as _
from app.models.sys import SysSetting
from app.exception import SmsException

from app.models.sys import SysSetting
from app.exception import SmsException

from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class SmsServiceFactory(object):
    """短信服务工厂类"""

    @staticmethod
    def get_smsservice():
        """获取短信服务对象"""

        # 加载短信服务支持配置
        vendor = SysSetting.query.\
            filter(SysSetting.key == 'sms_vendor').first()

        if vendor is None:
            raise SmsException(_(u'短信服务配置不存在'))
        mod = importlib.import_module(__name__)
        return getattr(mod, vendor.value)()


class SmsBaseService(object):
    """短信服务基类"""

    def __init__(self):
        # 服务类型key
        self.config_key = ''

        # 短信服务配置
        self.sms_config = None

        # 短信前缀（默认一店）
        self.sms_prefix = ""

        # 目标电话集[],例子['xxxxxx', 'xxxxxx']
        self.mobiles = None

        # 目标内容参数集[{'code':1234}, {'code':1345}]
        self.params = None

        # 短信模版id
        self.template_id = ""

        # 模版内容
        self.template_content = ''

        # 服务客户端
        self.client = None

        # 发送类型 single=单发  mutil=群发(不同内容) mutil_single=群发(内容一致)
        self.send_type = ''

        # 默认短信类型
        self.type_list = ['single', 'mutil_single', 'mutil']

        # 模版配置信息
        self.tpl_config = None

    def _init(self):
        """加载短信服务配置信息"""

        config = SysSetting.query.\
            filter(SysSetting.key == self.config_key).first()
        if not config:
            raise SmsException(_(u'短信配置不存在'))
        try:
            self.sms_config = json.loads(config.value)
        except Exception as e:
            raise SmsException(e)
        self.sms_prefix = self.sms_config['app_name']

    def _init_tpl(self):
        """加载本地模版配置"""

        config_tpl = SysSetting.query.\
            filter(SysSetting.key == 'config_sms_template').first()
        if config_tpl is None:
            raise SmsException(_(u'短信模版配置不存在'))
        try:
            self.tpl_config = json.loads(config_tpl.value)
        except Exception as e:
            raise SmsException(e)

    def _check_params(self):
        """检查公共参数, 之类扩展各自参数"""

        if not self.template_id:
            raise SmsException(_(u'模版ID不存在'))

        if not self.mobiles:
            raise SmsException(_(u'短信接收电话不存在'))

        if not self.params:
            raise SmsException(_(u'短信内容不存在'))

        if len(self.mobiles) > 1000:
            raise SmsException(_(u'最多同时发送1000个'))

        if not isinstance(self.mobiles, list):
            raise SmsException(_(u'电话参数格式不正确'))

        if not isinstance(self.params, list):
            raise SmsException(_(u'内容参数格式不正确'))

    def _get_tpl_content(self):
        """获取短信模版"""
        pass

    def _get_send_params(self):
        """装填请求参数，子类实现"""

        try:
            self._init()
            self._check_params()
        except SmsException as e:
            raise e
        pass

    def _do_sms_service(self):
        """执行短信服务"""
        pass

    def send_single_sms(self, mobiles, template_id, template_param):
        """发送单条短信"""
        pass

    def send_mutil_sms(self, mobiles, template_id, template_params):
        """发送多条短信"""
        pass

    def send_mutil_single_sms(self, mobiles, template_id, template_params):
        """发送多条短信"""
        pass

    def send_sms_code(self, mobile, code):
        """发送验证码"""
        pass

    def send_sms_order_shipping(self, mobiles, params):
        """订单发货信息"""
        pass


class YunPianSmsService(SmsBaseService):
    """云片短息服务"""

    def __init__(self):
        """初始化"""

        SmsBaseService.__init__(self)
        self.config_key = "config_sms_yunpian"
        self.api_key = ""

    def _init(self):
        """扩展父类配置加载"""

        super(YunPianSmsService, self)._init()
        self.api_key = self.sms_config['ak']
        if not self.api_key:
            raise SmsException(_(u'接口验证序号不存在'))
        self.client = YunpianClient(self.api_key)

    def _check_params(self):
        """扩展父类参数检查"""

        super(YunPianSmsService, self)._check_params()
        if not self.client:
            raise SmsException(_(u'服务执行对象不存在'))
        if self.send_type == self.type_list[2]:
            if len(self.mobiles) != len(self.params):
                raise SmsException(_(u'电话数与内容数不一致'))

    def _get_send_params(self):
        """转载请求参数"""

        super(YunPianSmsService, self)._get_send_params()
        # 参数处理，键需要是#key#的形式
        if self.send_type == self.type_list[2]:
            self._get_tpl_content()

        new_params = []
        if self.send_type != self.type_list[2]:
            for _param in self.params:
                temp = {}
                for key_name in _param.keys():
                    temp['#%s#' % key_name] = _param[key_name]
                new_params.append(urlencode(temp))
        else:
            for _param in self.params:
                tpl_content = self.template_content
                for key_name in _param.keys():
                    tpl_content = tpl_content.replace(
                        "#code#",
                        _param[key_name])
                new_params.append(tpl_content)
        self.params = new_params

        if self.send_type == self.type_list[0]:
            return {
                YC.MOBILE: self.mobiles[0],
                YC.TPL_ID: self.template_id,
                YC.TPL_VALUE: self.params[0]}
        if self.send_type == self.type_list[1]:
            return {
                YC.MOBILE: ','.join(self.mobiles),
                YC.TPL_ID: self.template_id,
                YC.TPL_VALUE: self.params[0]}
        if self.send_type == self.type_list[2]:
            return {
                YC.MOBILE: ','.join(self.mobiles),
                YC.TEXT: ','.join(self.params)}

        raise SmsException(_(u'短息类型不存在'))

    def _do_sms_service(self):
        """发送短信"""

        reqest_param = self._get_send_params()
        log_info(reqest_param)
        if self.send_type == self.type_list[0]:
            res = self.client.sms().tpl_single_send(reqest_param)

        if self.send_type == self.type_list[1]:
            res = self.client.sms().tpl_batch_send(reqest_param)

        if self.send_type == self.type_list[2]:
            res = self.client.sms().multi_send(reqest_param)

        if res is None:
            raise SmsException(_(u'发送失败'))
        if res.code() != 0:
            log_info('[YunPianSmsService]send_type:%s，code:%s，msg:%s，data:%s，prefix:%s' % (
                self.send_type, str(res.code()), res.msg(), (res.data() if res.data() else u'[]'), self.sms_prefix))
            raise SmsException(_(u'发送失败'))

    def _get_tpl_content(self):
        """获取短信模版内容"""

        tpl_res = self.client.tpl().get({
            'apikey': self.api_key,
            'tpl_id': self.template_id})
        if tpl_res.code() != 0 and tpl_res.data() is None:
            raise SmsException(_(u'模版获取失败'))
        self.template_content = tpl_res.data()['tpl_content']
        if not self.template_content:
            raise SmsException(_(u'模版获取失败'))

    def send_single_sms(self, mobiles, template_id, params):
        """短信单发"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[0]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_mutil_single_sms(self, mobiles, template_id, params):
        """短信群发(内容一致)"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[1]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_mutil_sms(self, mobiles, template_id, params):
        """短信群发(内容不一致)"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[2]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_sms_code(self, mobile, code):
        """发送短信验证码"""

        self._init_tpl()
        if not mobile and not code:
            raise SmsException(_(u'缺少电话或验证码'))
        try:
            self.send_single_sms(
                [mobile],
                self.tpl_config['code_tpl'],
                [{'code': code}])
        except SmsException as e:
            raise e
        return True

    def send_sms_order_shipping(self, mobiles, params):
        """发送发货订单信息"""
        self._init_tpl()
        try:
            self.send_mutil_sms(
                mobiles,
                self.tpl_config['order_shipping_tpl'],
                params)
        except SmsException as e:
            raise e
        return True


class AliSmsService(SmsBaseService):
    """阿里云短息服务"""

    def __init__(self):
        """初始化"""
        SmsBaseService.__init__(self)
        self.config_key = "config_sms_alisms"
        self.access_key_id = ""
        self.access_key_secret = ""

    def _init(self):
        """扩展父类配置加载"""

        super(AliSmsService, self)._init()
        self.access_key_id = self.sms_config['access_key_id']
        self.access_key_secret = self.sms_config['access_key_secret']
        if self.access_key_id is None:
            raise SmsException(_(u'应用公钥不存在'))
        if self.access_key_secret is None:
            raise SmsException(_(u'应用私钥不存在'))
        self.client = AcsClient(
            self.access_key_id,
            self.access_key_secret,
            'default')

    def _check_params(self):
        """扩展父类参数检查"""

        super(AliSmsService, self)._check_params()
        if not self.sms_prefix:
            raise SmsException(_(u'短信签名不存在1'))

    def _get_send_params(self):
        """装载请求参数"""

        super(AliSmsService, self)._get_send_params()
        params = {}
        if self.send_type != self.type_list[2]:
            try:
                single_template_param = json.dumps(self.params[0])
            except Exception as e:
                raise SmsException(_(u'参数转化失败'))
            params['PhoneNumbers'] = ','.join(self.mobiles)
            params['SignName'] = self.sms_prefix
            params['TemplateParam'] = single_template_param
        else:
            sign_names = [self.sms_prefix for _ in range(len(self.mobiles))]
            try:
                mobiles_json = json.dumps(self.mobiles)
                sign_names_json = json.dumps(self.sign_names)
                template_params_json = json.dumps(self.params)
            except Exception as e:
                raise SmsException(_(u'参数转化失败'))
            params['PhoneNumberJson'] = mobiles_json
            params['SignNameJson'] = sign_names_json
            params['TemplateParamJson'] = template_params_json
        return params

    def _do_sms_service(self):
        """发送短信"""

        request_params = self._get_send_params()
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.add_query_param('TemplateCode', self.template_id)
        if self.send_type != self.type_list[2]:
            request.set_action_name('SendSms')
            request.add_query_param(
                'PhoneNumbers', request_params['PhoneNumbers'])
            request.add_query_param(
                'SignName', request_params['SignName'])
            request.add_query_param(
                'TemplateParam', request_params['TemplateParam'])
        else:
            request.set_action_name('SendBatchSms')
            request.add_query_param(
                'PhoneNumberJson', request_params['PhoneNumberJson'])
            request.add_query_param(
                'SignNameJson', request_params['SignNameJson'])
            request.add_query_param(
                'TemplateParamJson', request_params['TemplateParamJson'])

        res = self.client.do_action(request)
        try:
            data = json.loads(res)
        except Exception as e:
            raise SmsException(_(u"发送失败"))

        if not data or data['Code'] != 'OK':
            log_info('[AliSmsService]send_type:%s，code:%s，msg:%s，data:%s，prefix:%s' % (
                self.send_type, data['Code'], data['Message'], data, self.sms_prefix))
            raise SmsException(_(u"发送失败"))

    def send_single_sms(self, mobiles, template_id, params):
        """短信单发"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[0]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_mutil_single_sms(self, mobiles, template_id, params):
        """短信群发(内容一致)"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[1]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_mutil_sms(self, mobiles, template_id, params):
        """短信群发(内容不一致)"""

        self.mobiles = mobiles
        self.template_id = template_id
        self.params = params
        self.send_type = self.type_list[2]
        try:
            self._do_sms_service()
        except SmsException as e:
            raise e
        return True

    def send_sms_code(self, mobile, code):
        """发送短信验证码"""

        self._init_tpl()
        if not mobile and not code:
            raise SmsException(_(u'缺少电话或验证码'))
        try:
            self.send_single_sms(
                [mobile],
                self.tpl_config['code_tpl'],
                [{'code': code}])
        except SmsException as e:
            raise e
        return True

    def send_sms_order_shipping(self, mobiles, params):
        """发送发货订单信息"""
        self._init_tpl()
        try:
            self.send_mutil_sms(
                mobiles,
                self.tpl_config['order_shipping_tpl'],
                params)
        except SmsException as e:
            raise e
        return True
