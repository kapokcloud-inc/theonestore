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
    url_for,
    g
)
from flask_babel import gettext as _

from app.database import db
from app.helpers import (
    render_template, 
    log_info,
    toint
)

from app.forms.admin.shipping import ShippingForm
from app.forms.admin.config import (
    SmsYunpianForm,
    SmsAlismsForm,
    StorageQiniuForm,
    StorageAliossForm
)
from app.models.shipping import Shipping
from app.models.sys import SysSetting


config = Blueprint('admin.config', __name__)

@config.route('/sms/yunpian', methods=["GET", "POST"])
def sms_yunpian():
    """配置云片短信"""
    g.page_title = _(u'云片短信')

    form = SmsYunpianForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_sms_yunpian').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
        form.fill_form(data=data)
    else:
        data = {'ak':form.ak.data, 'app_name':form.app_name.data}
        if form.validate_on_submit():
            if ss is None:
                ss = SysSetting()
                ss.key = 'config_sms_yunpian'
                db.session.add(ss)
            ss.value = json.dumps(data)
            db.session.commit()
            return redirect(url_for('admin.config.sms_yunpian'))

    return render_template('admin/config/sms_yunpian.html.j2', form=form, data=data)


@config.route('/sms/alisms', methods=["GET", "POST"])
def sms_alisms():
    """配置阿里短信"""
    g.page_title = _(u'阿里短信')

    form = SmsAlismsForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_sms_alisms').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
        form.fill_form(data=data)
    else:
        data = {'access_key_id':form.access_key_id.data,
                'access_key_secret':form.access_key_secret.data,
                'app_name':form.app_name.data}
        if form.validate_on_submit():
            if ss is None:
                ss = SysSetting()
                ss.key = 'config_sms_yunpian'
                db.session.add(ss)
            ss.value = json.dumps(data)
            db.session.commit()

            return redirect(url_for('admin.config.sms_alisms'))

    return render_template('admin/config/sms_alisms.html.j2', form=form, data=data)


@config.route('/storage/qiniu', methods=["GET", "POST"])
def storage_qiniu():
    """配置七牛存储"""
    g.page_title = _(u'七牛云存储')

    form = StorageQiniuForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_storage_qiniu').first()

    data = {}
    if request.method == "GET":
        if ss and ss.value:
            try:
                data = json.loads(ss.value)
            except Exception as identifier:
                pass
        form.fill_form(data=data)
        return render_template('admin/config/storage_qiniu.html.j2', form=form, data=data)

    data = {'access_key':form.access_key.data,
            'secret_key':form.secret_key.data,
            'bucket_name':form.bucket_name.data,
            'cname':form.cname.data}
    if not form.validate_on_submit():
        return render_template('admin/config/storage_qiniu.html.j2', form=form, data=data)

    if ss is None:
        ss = SysSetting()
        ss.key = 'config_storage_qiniu'
        db.session.add(ss)
    ss.value = json.dumps(data)
    db.session.commit()
    return redirect(url_for('admin.config.storage_qiniu'))


@config.route('/storage/alioss', methods=["GET", "POST"])
def storage_alioss():
    """配置阿里存储"""
    g.page_title = _(u'阿里云OSS存储')

    form = StorageAliossForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_storage_alioss').first()

    if request.method == "GET":
        try:
            data = json.loads(ss.value)
            form.fill_form(data=data)
        except Exception as e:
            data = {}
    else:
        data = {'access_key_id':form.access_key_id.data,
                'access_key_secret':form.access_key_secret.data,
                'bucket_name':form.bucket_name.data,
                'cname':form.cname.data}
        if form.validate_on_submit():
            if ss is None:
                ss = SysSetting()
                ss.key = 'config_storage_alioss'
                db.session.add(ss)
            ss.value = json.dumps(data)
            db.session.commit()
            return redirect(url_for('admin.config.storage_alioss'))

    return render_template('admin/config/storage_alioss.html.j2', form=form, data=data)


@config.route('/shipping')
def shipping():
    """快递"""
    g.page_title = _(u'快递')

    shipping_list = Shipping.query.\
                        order_by(Shipping.is_default.desc(), Shipping.is_enable.desc(), Shipping.sorting.desc()).all()

    return render_template('admin/config/shipping.html.j2', shipping_list=shipping_list)


@config.route('/shipping/detail/<int:shipping_id>')
def shipping_detail(shipping_id):
    """快递详情"""
    g.page_title = _(u'快递详情')

    shipping = Shipping.query.get_or_404(shipping_id)

    wtf_form                 = ShippingForm()
    wtf_form.is_enable.data  = shipping.is_enable
    wtf_form.is_default.data = shipping.is_default
    wtf_form.is_free.data    = 1 if shipping.free_limit_amount == 0 else 0
    log_info(wtf_form.is_free.data)

    return render_template('admin/config/shipping_detail.html.j2', wtf_form=wtf_form, shipping=shipping)


@config.route('/shipping/save', methods=['POST'])
def shipping_save():
    """保存快递"""
    g.page_title = _(u'保存快递')

    wtf_form    = ShippingForm()
    shipping_id = wtf_form.shipping_id.data
    shipping    = Shipping.query.get_or_404(shipping_id)

    if wtf_form.validate_on_submit():
        shipping.shipping_amount   = wtf_form.shipping_amount.data
        shipping.free_limit_amount = wtf_form.free_limit_amount.data
        shipping.is_enable         = wtf_form.is_enable.data
        shipping.is_default        = wtf_form.is_default.data
        shipping.sorting           = wtf_form.sorting.data

        if shipping.is_default == 1:
            _shipping_list = Shipping.query.\
                                filter(Shipping.shipping_id != shipping_id).\
                                filter(Shipping.is_default == 1).all()
            for _shipping in _shipping_list:
                _shipping.is_default = 0

        db.session.commit()

        return redirect(url_for('admin.config.shipping'))

    wtf_form.shipping_name.data = shipping.shipping_name
    shipping                    = wtf_form.data

    return render_template('admin/config/shipping_detail.html.j2', wtf_form=wtf_form, shipping=shipping)

