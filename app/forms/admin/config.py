# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    FileField,
    SelectField,
    TextAreaField
)
from wtforms.validators import (
    Required,
    Length,
    EqualTo,
    NumberRange
)

from app.forms import Form


class SmsYunpianForm(Form):
    ak = StringField(_name='ak', 
                    label=_(u'APIKEY'),
                    validators=[Required(message=_(u'请填写APIKEY'))])
    app_name = StringField(_name='app_name', 
                    label=_(u'短信前辍'),
                    description=_(u'例如：【一店】，则填写 一店，不需填写方括号'),
                    validators=[Required(message=_(u'请填写前缀'))])


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


class StorageAliossForm(Form):
    access_key_id = StringField(_name='access_key_id', 
                    label=_('AccessKey ID'),
                    description=_(u'<a target="_blank" href="https://help.aliyun.com/knowledge_detail/38738.html">AccessKey ID和AccessKey Secret 请见阿里云文档</a>'), 
                    validators=[Required(message=_(u'请填写ACCESSKEY'))])

    access_key_secret = StringField(_name='access_key_secret', 
                    label=_('AccessKey Secret'),
                    validators=[Required(message=_(u'请填写AccessKey Secret'))])

    bucket_name = StringField(_name='bucket_name', 
                    label=_(u'存储空间'), 
                    description=_(u'<a target="_blank" href="https://help.aliyun.com/document_detail/31883.html">存储空间 请见阿里云OSS文档</a>'), 
                    validators=[Required(message=_(u'请填写存储空间'))])

    cname = StringField(_name='cname', 
                    label=_(u'CDN加速域名'), 
                    description=_(u'<p>不需要填写https或者http开头，只需要填写域名</p><p>例如：static.theonestore.cn</p>'),
                    validators=[Required(message=_(u'请填写CDN加速域名'))])
