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
    HiddenField,
    BooleanField,
    SelectMultipleField
)
from wtforms.validators import (
    DataRequired as Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.helpers.date_time import current_timestamp


from app.models.coupon import CouponBatch
from app.forms import Form

class RechargeForm(Form):
    '''充值Form'''
    nickname         = StringField(_(u'用户名'),
                            render_kw={'readonly':'readonly'})

    avatar           = FileField(_(u'头像'),
                            validators=[
                            FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片')),
                        ],
                            render_kw={'class':'hide'}) 

    uid              = IntegerField(_(u'用户ID'),
                            validators=[
                                Required(message=_(u'请填写用户的UID')),
                                NumberRange(min=0, message=_(u'不能小于0'))
                            ],
                             render_kw={'readonly':'readonly'}
                        )

    recharge_amount  = DecimalField(_(u'充值金额'),
                            validators=[
                                Required(message=_(u'请填写正确的充值金额')),
                                NumberRange(min=0, message=_(u'金额不能小于0'))
                            ]
                        )

class CouponForm(Form):
    '''优惠券分发Form'''
    nickname         = StringField(_(u'用户名'),
                            render_kw={'readonly':'readonly'})

    avatar           = FileField(_(u'头像'),
                            validators=[
                            FileAllowed(UploadSet('images', IMAGES), message=_(u'只允许上传图片')),
                        ],
                            render_kw={'class':'hide'}) 

    uid              = IntegerField(_(u'用户ID'),
                            validators=[
                                Required(message=_(u'请填写用户的UID')),
                                NumberRange(min=0, message=_(u'不能小于0'))
                            ],
                             render_kw={'readonly':'readonly'}
                        )

    cb_id          = SelectField(_(u'优惠券'),
                            coerce=int,
                            validators=[
                                Required(message=_(u'请选择要派发的优惠券')),
                            ]
                        )
    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)

        _coupons   = db.session.query(CouponBatch.cb_id, CouponBatch.coupon_name).\
                                    filter(current_timestamp() <= CouponBatch.end_time).\
                                    filter(CouponBatch.give_num < CouponBatch.publish_num).\
                                    filter(CouponBatch.is_valid == 1).all()
        
        self.cb_id.choices = _coupons