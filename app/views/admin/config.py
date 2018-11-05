# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~

    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json
import os

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for,
    g,
    current_app
)
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict

from app.database import db
from app.helpers import (
    render_template,
    log_info,
    toint
)

from app.forms.admin.shipping import ShippingForm
from app.services.uploads import FileUploadService
from app.forms.admin.config import (
    WeixinMpForm,
    WeixinPayForm,
    WeixinOpenForm,
    SmsYunpianForm,
    SmsAlismsForm,
    StorageQiniuForm,
    StorageAliossForm,
    AftersalesServiceForm,
    WeixinBaseInfoForm,
    WeixinSortForm
)
from app.models.shipping import Shipping
from app.models.sys import SysSetting


config = Blueprint('admin.config', __name__)


@config.route('/mp', methods=['GET', 'POST'])
def mp():
    """微信公众号"""
    g.page_title = _(u'微信公众号')

    form = WeixinMpForm(CombinedMultiDict((request.files, request.form)))
    ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_mp').first()
    data = {}
    if ss:
        try:
            data = json.loads(ss.value)
        except Exception as e:
            pass

    if request.method == 'GET':
        form.fill_form(data=data)
        return render_template('admin/config/weixin_mp.html.j2', form=form)

    if not form.validate_on_submit():
        return render_template('admin/config/weixin_mp.html.j2', form=form)

    data['appid'] = form.appid.data
    data['secret'] = form.secret.data
    if ss is None:
        ss = SysSetting()
        ss.key = 'config_weixin_mp'
        db.session.add(ss)

    # 校验文件上传
    if form.mp_verify.data:
        mp_verify = secure_filename(form.mp_verify.data.filename)
        uploads_path = current_app.config['UPLOADED_FILES_DEST']
        form.mp_verify.data.save(os.path.join(uploads_path, mp_verify))
        mp_verify = '/'+mp_verify
        data['mp_verify'] = mp_verify

    ss.value = json.dumps(data)
    db.session.commit()
    return redirect(url_for('admin.index.success', title=_(u'设置微信公众号成功')))


@config.route('/weixinpay', methods=['GET', 'POST'])
def weixinpay():
    """微信支付"""
    g.page_title = _(u'微信支付')

    form = WeixinPayForm(CombinedMultiDict((request.files, request.form)))
    ss = SysSetting.query.filter(
        SysSetting.key == 'config_paymethod_weixin').first()
    data = {}
    try:
        data = json.loads(ss.value)
    except Exception as e:
        data = {}

    if request.method == 'GET':
        form.fill_form(data=data)
        form.apiclient_cert.data = data.get('apiclient_cert_url', '')
        form.apiclient_key.data = data.get('apiclient_key_url', '')
        return render_template('admin/config/weixinpay.html.j2', form=form)

    data = {'mch_id': form.mch_id.data, 'partner_key': form.partner_key.data,
            'apiclient_cert': data.get('apiclient_cert', ''), 'apiclient_key': data.get('apiclient_key', '')}
    if not form.validate_on_submit():
        form.apiclient_cert.data = data.get('apiclient_cert_url', '')
        form.apiclient_key.data = data.get('apiclient_key_url', '')
        return render_template('admin/config/weixinpay.html.j2', form=form)

    # 证书文件cert上传
    if form.apiclient_cert.data:
        apiclient_cert = secure_filename(form.apiclient_cert.data.filename)
        uploads_path = os.path.join(os.getcwd(), 'pem')
        cert_filename = os.path.join(uploads_path, apiclient_cert)
        if not os.path.exists(uploads_path):
            os.makedirs(uploads_path)
        form.apiclient_cert.data.save(cert_filename)
        data['apiclient_cert'] = cert_filename
        data['apiclient_cert_url'] = '/apiclient_cert.pem'

    # 证书文件key上传
    if form.apiclient_key.data:
        apiclient_key = secure_filename(form.apiclient_key.data.filename)
        uploads_path = os.path.join(os.getcwd(), 'pem')
        key_filename = os.path.join(uploads_path, apiclient_key)
        if not os.path.exists(uploads_path):
            os.makedirs(uploads_path)
        form.apiclient_key.data.save(key_filename)
        data['apiclient_key'] = key_filename
        data['apiclient_key_url'] = '/apiclient_key.pem'

    if ss is None:
        ss = SysSetting()
        ss.key = 'config_paymethod_weixin'
        db.session.add(ss)

    ss.value = json.dumps(data)
    db.session.commit()
    return redirect(url_for('admin.index.success', title=_(u'设置微信支付成功')))


@config.route('/weixinopen', methods=['GET', 'POST'])
def weixinopen():
    """微信开放平台"""
    g.page_title = _(u'微信开放平台')

    form = WeixinOpenForm()
    ss = SysSetting.query.filter(
        SysSetting.key == 'config_weixin_open').first()
    if request.method == 'GET':
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
        form.fill_form(data=data)
    else:
        data = {'appid': form.appid.data, 'secret': form.secret.data}
        if form.validate_on_submit():
            if ss is None:
                ss = SysSetting()
                ss.key = 'config_weixin_open'
                db.session.add(ss)
            ss.value = json.dumps(data)
            db.session.commit()
            return redirect(url_for('admin.index.success', title=_(u'设置微信开放平台成功')))

    return render_template('admin/config/weixinopen.html.j2', form=form)


@config.route('/weixin/baseinfo', methods=['GET', 'POST'])
def weixin_baseinfo():
    """基本信息"""
    g.page_title = _(u'基本信息')

    form = WeixinBaseInfoForm(CombinedMultiDict((request.files, request.form)))
    ss = SysSetting.query.filter(SysSetting.key == 'config_weixin_baseinfo').first()

    data = {}
    try:
        data = json.loads(ss.value)
    except Exception as e:
        data = {}

    if request.method == 'GET':
        form.fill_form(data=data)
        return render_template('admin/config/weixin_baseinfo.html.j2', form=form)

    if not form.validate_on_submit():
        return render_template('admin/config/weixin_baseinfo.html.j2', form=form)

    # 校验图片上传
    app_logo = ''
    if form.app_logo.data:
        fus = FileUploadService()
        log_info('上传的图片')
        log_info(fus)
        try:
            app_logo = fus.save_storage(form.app_logo.data, 'applogo')
        except Exception as e:
            form.app_logo.errors = (_(u'上传失败，请检查云存储配置'))
            return render_template('admin/item/weixin_baseinfo.html.j2', form=form)
    app_logo = app_logo if app_logo else data.get('app_logo','')
    data = {'app_name': form.app_name.data, 'app_logo': app_logo, 'app_recommend': form.app_recommend.data}
    # 配置表中没该key,先添加该key
    if ss is None:
        ss = SysSetting()
        ss.key = 'config_weixin_baseinfo'
        db.session.add(ss)

    ss.value = json.dumps(data)
    db.session.commit()
    return redirect(url_for('admin.index.success', title=_(u'设置基本信息成功')))

@config.route('/weixin/soet', methods=['GET', 'POST'])
def weixin_sort():
    """ 配置微信小程序 """

    g.page_title = _(u'微信小程序')

    form = WeixinSortForm()
    ss   = SysSetting.query.filter(SysSetting.key == 'config_weixin_sort').first()

    data = {}
    try:
        data = json.loads(ss.value)
    except Exception as e:
        data = {}

    if request.method == 'GET':
        form.fill_form(data=data)
        return render_template('admin/config/weixin_sort.html.j2', form=form)

    if not form.validate_on_submit():
        return render_template('admin/config/weixin_sort.html.j2', form=form)

    data = {'appid':form.appid.data, 'secret':form.secret.data}
    if ss is None:
        ss = SysSetting()
        ss.key = 'config_weixin_sort'
        db.session.add(ss)

    # 校验文件上传
    if form.sort_verify.data:
        sort_verify = secure_filename(form.sort_verify.data.filename)
        uploads_path = current_app.config['UPLOADED_FILES_DEST']
        form.sort_verify.data.save(os.path.join(uploads_path, sort_verify))
        sort_verify = '/'+sort_verify
        data['sort_verify'] = sort_verify

    ss.value = json.dumps(data)
    db.session.commit()
    return redirect(url_for('admin.index.success', title=_(u'设置微信小程序成功')))


    

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
                'endpoint':form.endpoint.data,
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

    # wtf_form                 = ShippingForm()
    # wtf_form.is_enable.data  = shipping.is_enable
    # wtf_form.is_default.data = shipping.is_default
    # wtf_form.is_free.data    = 1 if shipping.free_limit_amount == 0 else 0
    # log_info(wtf_form.is_free.data)
    form = ShippingForm()
    form.fill_form(obj=shipping)

    return render_template('admin/config/shipping_detail.html.j2', form=form, shipping=shipping)


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

    return render_template('admin/config/shipping_detail.html.j2', form=wtf_form, shipping=shipping)


@config.route('/aftersales_service', methods=['GET','POST'])
def aftersales_service():
    """售后服务"""
    g.page_title = _(u'售后服务')

    form = AftersalesServiceForm()
    ss = SysSetting.query.filter(SysSetting.key == 'config_aftersales_service').first()
    if request.method == 'GET':
        try:
            data = json.loads(ss.value)
        except Exception as e:
            data = {}
        form.fill_form(data=data)
    else:
        data = {'consignee_name':form.consignee_name.data, 'consignee_mobile':form.consignee_mobile.data, 'consignee_address':form.consignee_address.data}
        if form.validate_on_submit():
            if ss is None:
                ss = SysSetting()
                ss.key = 'config_aftersales_service'
                db.session.add(ss)
            ss.value = json.dumps(data)
            db.session.commit()
            return redirect(url_for('admin.index.success',title=_(u'设置售后地址成功')))
    
    return render_template('admin/config/aftersales_service.html.j2',form=form)
