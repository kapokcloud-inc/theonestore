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

from app.helpers import (
    render_template,
    log_info,
    toint
)
from app.helpers.user import (
    check_login,
    get_uid
)

from app.services.api.aftersales import (
    AfterSalesCreateService,
    AfterSalesStaticMethodsService
)

from app.services.api.order import (
    OrderStaticMethodsService
)

from app.helpers.date_time import current_timestamp

from app.forms.api.aftersales import AfterSalesForm
from app.database import db

from app.models.sys import SysSetting
from app.models.aftersales import (
    Aftersales,
    AftersalesLogs,
    AftersalesAddress
)

from app.models.order import (
    OrderAddress,
    OrderGoods
)

aftersales = Blueprint('pc.aftersales', __name__)

@aftersales.route('/')
def root():
    """pc站 - 售后服务记录"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    _data         = AfterSalesStaticMethodsService.aftersales(params,True)

    aftersales_status_text = {}
    for aftersale in _data['aftersales']:
        status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersale)
        aftersales_status_text[aftersale.aftersales_id] = status_text

    data = {'aftersales':_data['aftersales'], 'aftersales_status_text':aftersales_status_text,'pagination':_data['pagination']}
    return render_template('pc/aftersales/index.html.j2', **data)


@aftersales.route('/<int:aftersales_id>')
def detail(aftersales_id):
    """pc站 - 售后服务详情"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).filter(Aftersales.uid == uid).first()
    if not aftersales:
        return redirect(url_for('pc.index.pagenotfound'))
    
    logs       = AftersalesLogs.query.\
                            filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
                            order_by(AftersalesLogs.al_id.desc()).all()
        
    logs_time  = {}
    for log in logs:
        logs_time[log.al_type] = log.add_time

    status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersales)
    #回寄地址信息
    aftersales_service = {}
    if aftersales.check_status == 2:
        ss = SysSetting.query.filter(SysSetting.key == 'config_aftersales_service').first()
        if not ss:
            return redirect(url_for('pc.index.servererror'))
        
        try:
            aftersales_service = json.loads(ss.value)
        except Exception as e:
            return redirect(url_for('pc.index.servererror'))
    #换货收货地址
    address     = None
    if aftersales.aftersales_type == 3:
        address = AftersalesAddress.query.filter(AftersalesAddress.aftersales_id == aftersales_id).first()

    data = {'aftersales':aftersales, 'logs':logs, 'logs_time':logs_time,'status_text':status_text, 'action_code':action_code, 'aftersales_service':aftersales_service, 'aftersales_address':address}

    return render_template('pc/aftersales/detail.html.j2', **data)


@aftersales.route('/apply/step0/<int:order_id>')
def apply_step0(order_id):
    """pc站 - 申请售后服务-选择产品"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login_qrcode'))
    uid = get_uid()

    data                  = OrderStaticMethodsService.detail_page(order_id, uid)
    #pc端订单详情不支持再次购买，排除掉指令[5]
    data['code']= list(set(data['code'])-set([5]))

    #申请售后的存在多条售后记录
    aftersale_all         = db.session.query(Aftersales.goods_data,Aftersales.aftersales_id).\
                            filter(Aftersales.order_id == order_id).\
                            filter(Aftersales.status.in_([1,2])).all()
    data['aftersale_all'] = aftersale_all

    return render_template('pc/aftersales/apply_step0.html.j2', **data)


@aftersales.route('/apply/step1/')
def apply_step1():
    """pc站 - 申请售后服务-第一步"""

    if not check_login():
        session['weixin_login_url'] = request.url
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()
    
    order_id              = int(request.args.to_dict().get('order_id', '0'))
    og_id                 = int(request.args.to_dict().get('og_id', '0'))
    
    if order_id <= 0 and og_id <= 0:
        return redirect(url_for('pc.index.pagenotfound'))

    wtf_form              = AfterSalesForm()
    # order_id大于0则整单操作，否则指定商品操作
    if order_id > 0:
        ascs = AfterSalesCreateService(uid, order_id=order_id, og_id=0, quantity=1, aftersales_type=1, deliver_status=1)
        ret  = ascs._check_order()
        if not ret:
            if ascs.msg == u'售后状态错误' and ascs.aftersales:
                return redirect(url_for('pc.aftersales.detail', aftersales_id=ascs.aftersales.aftersales_id ))

            return redirect(url_for('pc.index.pagenotfound'))

        data = {'wtf_form':wtf_form, 'order_id':order_id, 'og_id':og_id, 
                'items':ascs.order_goods_list, 'goods_data':ascs.goods_data, 
                'refunds_amount':ascs.refunds_amount, 'current_time':current_timestamp(), 
                'aftersales_type':1, 'order_address':ascs.order_address}
        
        return render_template('pc/aftersales/apply_step1.html.j2', **data)
    else:
        aftersales_type     = 2
        ascs = AfterSalesCreateService(uid, order_id=0, og_id=og_id, quantity=1, aftersales_type=aftersales_type, deliver_status=1)
        ret  = ascs._check_order_goods()
        if not ret:
            if ascs.msg != u'超过有效退款时间':
                return redirect(url_for('pc.index.pagenotfound'))

            aftersales_type = 3
            ascs            = AfterSalesCreateService(uid, order_id=0, og_id=og_id, quantity=1, aftersales_type=aftersales_type, deliver_status=1)
            ret             = ascs._check_order_goods()
            if not ret:
                return redirect(url_for('pc.index.pagenotfound'))

        data = {'wtf_form':wtf_form, 'order_id':order_id, 'og_id':og_id,
                'items':ascs.order_goods_list, 'goods_data':ascs.goods_data,
                'refunds_amount':ascs.refunds_amount, 'aftersales_type':aftersales_type, 
                'current_time':current_timestamp(), 'order_address':ascs.order_address}
                
        return render_template('pc/aftersales/apply_step1.html.j2', **data)


@aftersales.route('/apply/step2')
def apply_step2():
    """pc站 - 申请售后服务-第二步"""
    data = request.args.to_dict()

    return render_template('pc/aftersales/apply_step2.html.j2', **data)


@aftersales.route('/apply/step3/')
def apply_step3():
    """pc站 - 申请售后服务-第三步"""
    data = request.args.to_dict()

    return render_template('pc/aftersales/apply_step3.html.j2', **data)
