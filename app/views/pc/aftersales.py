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

from app.forms.api.aftersales import AfterSalesForm

from app.models.aftersales import (
    Aftersales,
    AftersalesLogs
)

from app.models.order import (
    OrderAddress
)

aftersales = Blueprint('pc.aftersales', __name__)

@aftersales.route('/')
def root():
    """pc站 - 售后服务记录"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    _data         = AfterSalesStaticMethodsService.aftersales(params)

    aftersales_status_text = {}
    for aftersale in _data['aftersales']:
        status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersale)
        aftersales_status_text[aftersale.aftersales_id] = status_text

    data = {'aftersales':_data['aftersales'], 'aftersales_status_text':aftersales_status_text}
    return render_template('pc/aftersales/index.html.j2', **data)


@aftersales.route('/<int:aftersales_id>')
def detail(aftersales_id):
    """pc站 - 售后服务详情"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).filter(Aftersales.uid == uid).first()
    if not aftersales:
        return redirect(request.headers['Referer'])
    
    log = AftersalesLogs.query.\
            filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
            order_by(AftersalesLogs.al_id.desc()).all()

    status_text, action_code = AfterSalesStaticMethodsService.aftersale_status_text_and_action_code(aftersales)

    order_address = OrderAddress.query.filter(OrderAddress.order_id == aftersales.order_id).first()

    data = {'aftersales':aftersales, 'log':log, 'status_text':status_text, 'action_code':action_code,'order_address':order_address}
    return render_template('pc/aftersales/detail.html.j2', **data)


@aftersales.route('/apply/step0/<int:order_id>')
def apply_step0(order_id):
    """pc站 - 申请售后服务-选择产品"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    data = OrderStaticMethodsService.detail_page(order_id, uid)
    #pc端订单详情不支持再次购买，排除掉指令[5]
    data['code']= list(set(data['code'])-set([5]))

    return render_template('pc/aftersales/apply_step0.html.j2', **data)


@aftersales.route('/apply/step1')
def apply_step1():
    """pc站 - 申请售后服务-第一步"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_id = toint(request.args.get('order_id', '0'))
    og_id    = toint(request.args.get('og_id', '0'))

    

    return render_template('pc/aftersales/apply_step1.html.j2')


@aftersales.route('/apply/step2')
def apply_step2():
    """pc站 - 申请售后服务-第二步"""

    return render_template('pc/aftersales/apply_step2.html.j2')


@aftersales.route('/apply/step3')
def apply_step3():
    """pc站 - 申请售后服务-第三步"""

    return render_template('pc/aftersales/apply_step3.html.j2')
