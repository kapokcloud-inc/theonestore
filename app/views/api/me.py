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
    get_uid,
    set_user_session
)

from app.services.response import ResponseJson

from app.forms.api.me import (
    ProfileForm,
    AddressForm
)

from app.models.user import (
    User,
    UserAddress
)


me = Blueprint('api.me', __name__)

resjson = ResponseJson()
resjson.module_code = 13

@me.route('/update', methods=["POST"])
def update():
    """更新个人资料"""
    resjson.action_code = 10
    
    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    wtf_form     = ProfileForm()
    current_time = current_timestamp()

    if not wtf_form.validate_on_submit():
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(11, msg)

    data = {'nickname':wtf_form.nickname.data, 'avatar':wtf_form.avatar.data,
            'gender':wtf_form.gender.data, 'update_time':current_time}

    user = User.query.get(uid)
    model_update(user, data, commit=True)

    set_user_session(user)

    return resjson.print_json(0, u'ok')

@me.route('/address-save', methods=["POST"])
def address_save():
    """保存地址"""
    resjson.action_code = 11

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
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
        data         = {'uid':uid, 'is_default':1, 'add_time':current_time}
        user_address = model_create(UserAddress, data)

    if is_default == -1:
        is_default = user_address.is_default

    data = {'name':wtf_form.name.data, 'mobile':wtf_form.mobile.data, 'province':wtf_form.province.data,
            'city':wtf_form.city.data, 'district':wtf_form.district.data, 'address':wtf_form.address.data,
            'is_default':is_default, 'update_time':current_time}

    if is_default == 1:
        default = UserAddress.query.filter(UserAddress.uid == uid).filter(UserAddress.is_default == 1).first()
        if default and default.ua_id != ua_id:
            default.is_default = 0

    user_address = model_update(user_address, data)

    db.session.commit()

    return resjson.print_json(0, u'ok', {'ua_id':user_address.ua_id})


@me.route('/address-remove')
def address_remove():
    """删除地址"""
    resjson.action_code = 12

    if not check_login():
        return resjson.print_json(resjson.NOT_LOGIN)
    uid = get_uid()

    ua_id = toint(request.args.get('ua_id', '0'))

    # 检查
    user_address = UserAddress.query.filter(UserAddress.ua_id == ua_id).filter(UserAddress.uid == uid).first()
    if not user_address:
        return resjson.print_json(0, u'ok')

    model_delete(user_address, commit=True)

    return resjson.print_json(0, u'ok')

@me.route('/address/list', methods=["GET"])
def address_list():
    """地址管理"""

    resjson.action_code = 13

    # if not check_login():
    #     return resjson.print_json(resjson.NOT_LOGIN)
    # uid = get_uid()

    address_list = UserAddress.query.filter(UserAddress.uid == 1).order_by(UserAddress.is_default.desc()).all()
    
    data = {'address_list': address_list}
    return resjson.print_json(0, u'ok', data)