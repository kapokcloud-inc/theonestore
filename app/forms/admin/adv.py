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
from flask_wtf.file import (
    FileField, 
    FileAllowed, 
    FileRequired, 
    FileStorage
)
from flask_uploads import (
    UploadSet,
    IMAGES
)
from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    SelectField,
    TextAreaField,
    DateField,
    HiddenField,
    BooleanField
)
from wtforms.validators import (
    Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange,
    ValidationError
)

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.forms import Form


class checkTtype(object):
    def __init__(self, message=_(u'请完善跳转信息或填写外部链接')):
        self.message = message

    def __call__(self, form, field):
        if field.data <= 0 and form.url.data == '':
            raise ValidationError(self.message)


class checkTid(object):
    def __init__(self, message=_(u'请填写跳转目标')):
        self.message = message

    def __call__(self, form, field):
        if field.data <= 0 and form.ttype.data > 0:
            raise ValidationError(self.message)


class checkUrl(object):
    def __init__(self, message=_(u'请完善跳转信息或填写外部链接')):
        self.message = message

    def __call__(self, form, field):
        if field.data == '' and form.ttype.data <= 0:
            raise ValidationError(self.message)


class AdvForm(Form):
    """广告form"""
    adv_id  = HiddenField(default=0)

    ac_id   = SelectField(
                    _(u'分类'),
                    coerce=int,
                    choices=[(1, _(u'首页Banner'))],
                    validators=[
                        Required(message=_(u'请选择分类'))]
                )

    platform_type = SelectField(
                    _(u'平台类型'),
                    coerce=int,
                    choices=[ (1, _(u'移动端')), (2, _(u'PC端'))],
                    validators=[
                        Required(message=_(u'请选择平台类型'))]
                )

    img     = FileField(
                    _(u'封面原图'),
                    description=_(u'电脑端图片最佳尺寸1170x440<br>移动端图片最佳尺寸1080x540'),
                    validators=[
                        FileRequired(_(u'文件未上传')), 
                        FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片'))
                    ]
                )

    desc    = StringField(_(u'简介'))

    ttype   = SelectField(
                    _(u'跳转类型'),
                    coerce=int,
                    choices=[(0, _(u'请选择')),
                        (1, _(u'商品详情页')),
                        (2, _(u'分类商品列表页')),
                        (3, _(u'更多热卖商品列表页')),
                        (4, _(u'更多推荐商品列表页'))],
                    validators=[
                        checkTtype()]
                )

    tid     = IntegerField(_(u'跳转目标'), default=0, validators=[checkTid()])

    url     = StringField(_(u'外部链接'), validators=[checkUrl()])

    sorting = StringField(_(u'排序'))

    is_show = BooleanField(_(u'是否显示'), false_values=(0, '0', ''))

