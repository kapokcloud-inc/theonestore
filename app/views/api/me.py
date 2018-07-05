# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import (
    Blueprint,
    request
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    model_create,
    model_update,
    model_delete,
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.response import ResponseJson

from app.forms.api.me import AddressForm

from app.models.user import UserAddress


me = Blueprint('api.me', __name__)

resjson = ResponseJson()
resjson.module_code = 13

@me.route('/address/save', methods=["POST"])
def address_save():
    """保存地址"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))
    uid = get_uid()

    wtf_form     = AddressForm()
    current_time = current_timestamp()

    if not wtf_form.validate_on_submit():
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    is_default = toint(request.form.get('is_default', '-1'))
    if is_default not in [-1,0,1]:
        return resjson.print_json(resjson.PARAM_ERROR)

    ua_id = wtf_form.ua_id.data
    if ua_id:
        user_address = UserAddress.query.filter(UserAddress.ua_id == ua_id).filter(UserAddress.uid == uid).first()
        if not user_address:
            return resjson.print_json(12, _(u'收货地址不存在'))
    else:
        data         = {'uid':uid, 'add_time':current_time}
        user_address = model_create(UserAddress, data)

    data = {'name':wtf_form.name.data, 'mobile':wtf_form.mobile.data, 'province':wtf_form.province.data,
            'city':wtf_form.city.data, 'district':wtf_form.district.data, 'address':wtf_form.address.data,
            'update_time':current_time}

    default = UserAddress.query.filter(UserAddress.uid == uid).first()
    if not default:
        is_default = 1

    if is_default == 0:
        data['is_default'] = 1
    elif is_default == 1:
        default = UserAddress.query.filter(UserAddress.uid == uid).filter(UserAddress.is_default == 1).first()
        if default.ua_id != ua_id:
            default.is_default = 0

        data['is_default'] = 1

    user_address = model_update(user_address, data)

    db.session.commit()

    return resjson.print_json(0, u'ok', {'ua_id':user_address.ua_id})
