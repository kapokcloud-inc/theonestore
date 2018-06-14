# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _

from wtforms.validators import ValidationError


class NotExist(object):
    """
    检查记录是否存在
    用法: NotExist(CouponBatch, CouponBatch.cb_id, message=_(u'优惠券不存在')
    """
    def __init__(self, model, field, message=_(u'This element already exists.')):
        self.model   = model
        self.field   = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if not check:
            raise ValidationError(self.message)

