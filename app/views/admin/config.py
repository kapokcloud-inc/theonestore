# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)
from flask_babel import gettext as _

from app.database import db
from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.services.admin.config import (
    SmsYunpianForm,
    SmsAlismsForm,
    StorageQiniuForm,
    StorageAliossForm
)
from app.models.sys import SysSetting


config = Blueprint('admin.config', __name__)

@config.route('/sms/yunpian', methods=["GET", "POST"])
def sms_yunpian():
    """配置云片短信"""

    form = SmsYunpianForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_sms_yunpian').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
    else:
        data = {'ak':form.ak.data, 'app_name':form.app_name.data}
        if form.validate_on_submit():
            ss.value = json.dumps(data)
            db.session.commit()

            return redirect(url_for('admin.config.sms_yunpian'))

    return render_template('admin/config/sms_yunpian.html.j2', form=form, data=data)


@config.route('/sms/alisms', methods=["GET", "POST"])
def sms_alisms():
    """配置阿里短信"""

    form = SmsAlismsForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_sms_alisms').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
    else:
        data = {'access_key_id':form.access_key_id.data,
                'access_key_secret':form.access_key_secret.data,
                'app_name':form.app_name.data}
        if form.validate_on_submit():
            ss.value = json.dumps(data)
            db.session.commit()

            return redirect(url_for('admin.config.sms_alisms'))

    return render_template('admin/config/sms_alisms.html.j2', form=form, data=data)


@config.route('/storage/qiniu', methods=["GET", "POST"])
def storage_qiniu():
    """配置七牛存储"""

    form = StorageQiniuForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_storage_qiniu').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
    else:
        data = {'access_key':form.access_key.data,
                'secret_key':form.secret_key.data,
                'bucket_name':form.bucket_name.data,
                'cname':form.cname.data}
        if form.validate_on_submit():
            ss.value = json.dumps(data)
            db.session.commit()

            return redirect(url_for('admin.config.storage_qiniu'))

    return render_template('admin/config/storage_qiniu.html.j2', form=form, data=data)


@config.route('/storage/alioss', methods=["GET", "POST"])
def storage_alioss():
    """配置七牛存储"""

    form = StorageAliossForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_storage_alioss').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
    else:
        data = {'access_key_id':form.access_key_id.data,
                'access_key_secret':form.access_key_secret.data,
                'bucket_name':form.bucket_name.data,
                'cname':form.cname.data}
        if form.validate_on_submit():
            ss.value = json.dumps(data)
            db.session.commit()

            return redirect(url_for('admin.config.storage_alioss'))

    return render_template('admin/config/storage_alioss.html.j2', form=form, data=data)
