# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import (
    request,
    Blueprint,
    json,
    session
)
from hashlib import sha256

from flask_babel import gettext as _
from flask_wtf.csrf import generate_csrf

from app.database import db

from app.helpers import (
    log_info,
    toint,
    randomstr
)
from app.exception import TheonestoreException
from app.models.auth import AdminUsers
from app.helpers.date_time import current_timestamp
from app.models.sys import SysSetting
from app.services.response import ResponseJson
from app.services.sms import SmsServiceFactory
from app.exception import SmsException

sys = Blueprint('api.sys', __name__)

resjson = ResponseJson()
resjson.module_code = 22


@sys.route('/csrf-token', methods=['GET'])
def csrf_token():
    """获取csrf_token"""
    resjson.action_code = 10

    csrf_token = generate_csrf()

    return resjson.print_json(0, u'ok', {'csrf_token': csrf_token})


@sys.route('/sms_code', methods=['GET', 'POST'])
def sms_code():
    """获取短信验证码"""
    resjson.action_code = 10

    mobile = request.form.get('mobile', '').strip()
    log_info(mobile)
    if not mobile:
        return resjson.print_json(11, _(u'请输入手机号'))

    if len(mobile) != 11:
        return resjson.print_json(12, _(u'请输入正确的手机号'))

    # 随机生成4位验证码,并session保存
    code = randomstr(4, 1)
    expire_time = current_timestamp() + 300
    sms = SmsServiceFactory.get_smsservice()
    try:
        sms.send_sms_code(mobile, code)
        # 本地缓存
        session['code_expire_time'] = expire_time
        session['code'] = code
        session['code_mobile'] = mobile
    except SmsException as e:
        log_info(e.msg)
        return resjson.print_json(12, _(u'获取验证码失败'))

    return resjson.print_json(0, u'ok')


@sys.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """重置密码"""

    resjson.action_code = 11

    mobile = session.get('code_mobile', '')
    expire_time = session.get('code_expire_time', 0)
    key_code = session.get('code', '')

    form = request.form
    new_password = form.get('new_password', '').strip()
    again_password = form.get('again_password', '').strip()
    code = form.get('code', '').strip()

    admin_user = AdminUsers.query.filter(AdminUsers.mobile == mobile).first()
    try:
        if not admin_user:
            raise TheonestoreException(_(u'用户不存在'))
        if new_password != again_password:
            raise TheonestoreException(_(u'密码不一致'))
        if expire_time < current_timestamp():
            raise TheonestoreException(_(u'验证码已过期'))
        if key_code != code:
            raise TheonestoreException(_(u'验证码不正确'))
    except TheonestoreException as e:
        log_info(e.msg)
        return resjson.print_json(12, e.msg)

    sha256_password = sha256(new_password.encode('utf8')).hexdigest()
    admin_user.password = sha256((sha256_password+admin_user.salt).encode('utf8')).hexdigest()
    log_info(admin_user.password)
    db.session.commit()

    session['code_expire_time'] = None
    session['code'] = None
    session['code_mobile'] = None

    return resjson.print_json(0, u'ok')
