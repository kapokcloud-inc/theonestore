# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm
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
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)


class SmsYunpianForm(FlaskForm):
    ak       = StringField('ak', validators=[Required(message=_(u'请填写apikey'))])
    app_name = StringField('app_name', validators=[Required(message=_(u'请填写前缀'))])


class SmsAlismsForm(FlaskForm):
    access_key_id     = StringField('access_key_id', validators=[Required(message=_(u'请填写Access Key ID'))])
    access_key_secret = StringField('access_key_secret', validators=[Required(message=_(u'请填写Access Key Secret'))])
    app_name          = StringField('app_name', validators=[Required(message=_(u'请填写前缀'))])


class StorageQiniuForm(FlaskForm):
    access_key  = StringField('access_key', validators=[Required(message=_(u'请填写ACCESS KEY'))])
    secret_key  = StringField('secret_key', validators=[Required(message=_(u'请填写SECRET KEY'))])
    bucket_name = StringField('bucket_name', validators=[Required(message=_(u'请填写存储空间'))])
    cname       = StringField('cname', validators=[Required(message=_(u'请填写融合CDN加速域名'))])


class StorageAliossForm(FlaskForm):
    access_key_id     = StringField('access_key_id', validators=[Required(message=_(u'请填写Access Key ID'))])
    access_key_secret = StringField('access_key_secret', validators=[Required(message=_(u'请填写Access Key Secret'))])
    bucket_name       = StringField('bucket_name', validators=[Required(message=_(u'请填写存储空间'))])
    cname             = StringField('cname', validators=[Required(message=_(u'请填写融合CDN加速域名'))])

