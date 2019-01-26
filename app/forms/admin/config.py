# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_wtf.file import (
    FileField, 
    FileAllowed, 
    FileRequired
)
from flask_uploads import (
    UploadSet, 
    TEXT, 
    IMAGES
)

from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    SelectField,
    TextAreaField,
    BooleanField
)
from wtforms.validators import (
    Required,
    Length,
    EqualTo,
    NumberRange,
)

from app.forms import Form

class WeixinMpForm(Form):
    appid = StringField(label=_(u'开发者(AppID)'),
                    description=_(u'如：wxf7337ac7caaac670<br>请查看您的公众号 “开发->基本设置” '),
                    validators=[Required(message=_(u'请填写开发者(AppID)'))])

    secret = StringField(label=_(u'开发者密码(AppSecret)'),
                    description=_(u'如：b1946ac92492d2347c6235b4d2611184<br>请查看您的公众号 “开发->基本设置”'),
                    validators=[Required(message=_(u'请填写开发者密码(AppSecret)'))])

    mp_verify = FileField(_(u'公众号校验文件'), 
                    description=_(u'如：MP_verify_zprDbONIS74q99hQ.txt<br>请前往您的公众号 “设置 -> 公众号设置 -> 功能设置 -> 业务域名” 下载校验文件'), 
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('text', TEXT), message=_(u'只允许上传txt文本文件'))
                ])


class WeixinPayForm(Form):
    mch_id = StringField(label=_(u'微信支付商户号'),
                    description=_(u'如：1400590602，请前往您的商户平台 "帐户中心 -> 帐户设置 -> 商户信息 -> 基本帐户信息"'),
                    validators=[Required(message=_(u'请填写微信支付商户号'))])
    
    partner_key = StringField(label=_(u'微信支付商户密钥'),
                    description=_(u'请前往您的商户平台 "帐户中心 -> 帐户设置 -> API安全 -> API密钥"'),
                    validators=[Required(message=_(u'请填写微信支付商户密钥'))])

    apiclient_cert = FileField(_(u'商户证书cert'), 
                    description=_(u'如：apiclient_cert.pem<br>请前往您的商户平台 “帐户中心 -> 帐户设置 -> API安全 -> API证书” 下载证书文件'), 
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('pem', ('pem',)), message=_(u'只允许上传pem后辍文件'))
                ])
    
    apiclient_key = FileField(_(u'商户证书key'), 
                    description=_(u'如：apiclient_key.pem<br>请前往您的商户平台 “帐户中心 -> 帐户设置 -> API安全 -> API证书” 下载证书key文件'), 
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('pem', ('pem',)), message=_(u'只允许上传pem后辍文件'))
                ])
    

class WeixinOpenForm(Form):
    appid = StringField(label=_(u'微信开放平台(AppID)'),
                    description=_(u'登录微信开放平台，"管理中心 -> 网站应用 -> 应用详情"查看AppID。若还没有申请应用，请在微信开放平台申请"网站应用"。'),
                    validators=[Required(message=_(u'请填写微信开放平台(AppID)'))])

    secret = StringField(label=_(u'微信开放平台密码(AppSecret)'),
                    description=_(u'登录微信开放平台，"管理中心 -> 网站应用 -> 应用详情"查看AppSecret。若还没有申请应用，请在微信开放平台申请"网站应用"。'),
                    validators=[Required(message=_(u'请填写微信开放平台密码(AppSecret)'))])

class InfoBaseForm(Form):
    app_name = StringField(
                        _name='app_name',
                        label=_(u'应用名称'),
                        description=_(u'请设置应用的名称，如：一店、京东、天猫等'),
                        validators=[Required(message=_(u'请填写应用名称'))]
                        )

    app_logo = FileField(
                    _(u'logo图标'),
                    description=_(u'请上传不小于400x400的正方形图片'),
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片'))
                    ]
                )

    app_recommend = StringField(
                        _name='app_recommend',
                        label=_(u'一句话简介'),
                        description=_(u'请用一句话描述你的应用'),
                        validators=[Required(message=_(u'请用一句描述应用'))]
                        )
                    
class WeixinSortForm(Form):
    appid = StringField(label=_(u'小程序ID(AppID)'),
                    description=_(u'如：wxf7337ac7caaac670<br>请查看您的小程序 “设置->开发设置 '),
                    validators=[Required(message=_(u'请填写小程序ID(AppID)'))])

    secret = StringField(label=_(u'小程序密钥(AppSecret)'),
                    description=_(u'如：b1946ac92492d2347c6235b4d2611184<br>请查看您的小程序 “设置->开发设置'),
                    validators=[Required(message=_(u'请填写小程序密钥(AppSecret)'))])

    sort_verify = FileField(_(u'小程序校验文件'), 
                    description=_(u'如：sort_verify_zprDbONIS74q99hQ.txt<br>请前往您的小程序 “设置 -> 开发设置 -> 服务器域名” 下载校验文件'), 
                    validators=[
                        FileAllowed(UploadSet('text', TEXT), message=_(u'只允许上传txt文本文件'))
                ])

class SmsYunpianForm(Form):
    ak = StringField(_name='ak', 
                    label=_(u'APIKEY'),
                    validators=[Required(message=_(u'请填写APIKEY'))])
    app_name = StringField(_name='app_name', 
                    label=_(u'短信前辍'),
                    description=_(u'例如：【一店】，则填写 一店，不需填写方括号'),
                    validators=[Required(message=_(u'请填写前缀'))])

    is_use      = BooleanField(_(u'是否显示'), 
                    description=_(u'注意：使用云片短信，会自动禁用阿里云短信'),
                    false_values=(0, '0', '', 'sms_alisms'),
                    default='')


class SmsAlismsForm(Form):
    access_key_id = StringField(_name='access_key_id', 
                    label=_(u'AccessKey ID'),
                    description=_(u'<a target="_blank" href="https://help.aliyun.com/knowledge_detail/38738.html">AccessKey ID和AccessKey Secret 请见阿里云文档</a>'), 
                    validators=[Required(message=_(u'请填写ACCESSKEY'))])

    access_key_secret = StringField(_name='access_key_secret', 
                    label=_(u'AccessKey Secret'),
                    validators=[Required(message=_(u'请填写AccessKey Secret'))])

    app_name = StringField(_name='app_name', 
                    label=_(u'短信前辍'), 
                    description=_(u'例如：【一店】，则填写 一店，不需填写方括号'), 
                    validators=[Required(message=_(u'请填写短信前缀'))])

    is_use      = BooleanField(_(u'是否启用'), 
                    description=_(u'注意：使用阿里云短信，会自动禁用云片'),
                    false_values=(0, '0', '', 'sms_yunpian'), 
                    default='')


class StorageQiniuForm(Form):
    access_key = StringField('access_key', 
                    description=_(u'<a target="_blank" href="https://developer.qiniu.com/kodo/kb/1334/the-access-key-secret-key-encryption-key-safe-use-instructions">详情请见七牛文档</a>'), 
                    validators=[Required(message=_(u'请填写ACCESS KEY'))])

    secret_key = StringField('secret_key', 
                    validators=[Required(message=_(u'请填写SECRET KEY'))])

    bucket_name = StringField(_name='bucket_name', 
                    label=_(u'存储空间'), 
                    validators=[Required(message=_(u'请填写存储空间'))])

    cname = StringField(_name='cname', 
                    label=_(u'CDN加速域名'), 
                    description=_(u'<p>不需要填写https或者http开头，只需要填写域名</p><p>例如：static.theonestore.cn</p>'),
                    validators=[Required(message=_(u'请填写CDN加速域名'))])

    is_use = BooleanField(_(u'是否启用'), 
                    description=_(u'注意：使用七牛云存储，会自动禁用阿里云'),
                    false_values=(0, '0', '', 'aliyunoss'), 
                    default='')


class StorageAliossForm(Form):
    access_key_id = StringField(label=_('AccessKey ID'),
                    description=_(u'<a target="_blank" href="https://help.aliyun.com/knowledge_detail/38738.html">AccessKey ID和AccessKey Secret 请见阿里云文档</a>'), 
                    validators=[Required(message=_(u'请填写ACCESSKEY'))])

    access_key_secret = StringField(label=_('AccessKey Secret'),
                    validators=[Required(message=_(u'请填写AccessKey Secret'))])

    bucket_name = StringField(label=_(u'存储空间'), 
                    description=_(u'<a target="_blank" href="https://help.aliyun.com/document_detail/31883.html">存储空间 请见阿里云OSS文档</a>'),
                    validators=[Required(message=_(u'请填写存储空间'))])

    endpoint = StringField(label=_(u'EndPoint（地域节点）'), 
                    description=_(u'请登录你的阿里云OSS查看地域节点EndPoint'),
                    validators=[Required(message=_(u'请填写EndPoint（地域节点）'))])

    cname = StringField(label=_(u'CDN加速域名'), 
                    description=_(u'<p>不需要填写https或者http开头，只需要填写域名</p><p>例如：static.theonestore.cn</p>'),
                    validators=[Required(message=_(u'请填写CDN加速域名'))])

    is_use = BooleanField(_(u'是否启用'),
                    description=_(u'注意：使用阿里云存储，会自动禁用七牛云'),
                    false_values=(0, '0', '', 'qiniu'), 
                    default='')

class ShippingServiceForm(Form):
    customer = StringField(label= _(u'公司编号'),
                    description = _(u'<p>快递100分配给贵司的公司编号<br>请前往快递100开通服务 “快递接口(API)->接口申请->立即开通</p>'),
                    validators  = [Required(message=_(u'请填写快递100分配给贵司的公司编号'))])
    
    key      = StringField(label= _(u'授权key'),
                    description = _(u'<p>快递100分配给贵司的授权key<br>请前往快递100开通服务 “快递接口(API)->接口申请->立即开通</p>'),
                    validators  = [Required(message=_(u'请填写快递100分配给贵司的授权key'))])

class AftersalesServiceForm(Form):
    consignee_name    = StringField(label=_(u'售后收货负责人/部门'),
                        description=_(u'售后服务，用户"退货/换货"寄回商品的联系人/部门'), 
                        validators=[Required(message=_(u'请填写收货人'))])

    consignee_mobile  = StringField(label=_(u'联系电话'),
                        description=_(u'很重要，能联系到的负责人/部门电话'), 
                        validators=[Required(message=_(u'请填写收货人电话'))])

    consignee_address = StringField(label=_(u'完整地址'),
                        description=_(u'如：广东省深圳市南山区西丽大学城云谷2期8栋510'), 
                        validators=[Required(message=_(u'请填写收货人地址'))])

    