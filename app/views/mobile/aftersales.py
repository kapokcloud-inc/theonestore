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

from app.forms.api.aftersales import AfterSalesForm

from app.models.aftersales import (
    Aftersales,
    AftersalesLogs
)


aftersales = Blueprint('mobile.aftersales', __name__)

@aftersales.route('/')
def root():
    """手机站 - 售后服务列表"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    aftersales    = AfterSalesStaticMethodsService.aftersales(params)
    paging_url    = url_for('mobile.aftersales.paging', **request.args)

    data = {'aftersales':aftersales, 'paging_url':paging_url}
    return render_template('mobile/aftersales/index.html.j2', **data)


@aftersales.route('/paging')
def paging():
    """加载分页"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    params        = request.args.to_dict()
    params['uid'] = uid
    aftersales    = AfterSalesStaticMethodsService.aftersales(params)

    return render_template('mobile/aftersales/paging.html.j2', aftersales=aftersales)


@aftersales.route('/<int:aftersales_id>')
def detail(aftersales_id):
    """手机站 - 售后服务详情"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).filter(Aftersales.uid == uid).first()
    if not aftersales:
        return redirect(request.headers['Referer'])
    
    log = AftersalesLogs.query.\
            filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
            order_by(AftersalesLogs.al_id.desc()).first()

    return render_template('mobile/aftersales/detail.html.j2', aftersales=aftersales, log=log)


@aftersales.route('/track/<int:aftersales_id>')
def track(aftersales_id):
    """手机站 - 售后服务流水跟踪"""

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    aftersales = Aftersales.query.filter(Aftersales.aftersales_id == aftersales_id).filter(Aftersales.uid == uid).first()
    if not aftersales:
        return redirect(request.headers['Referer'])
    
    logs = AftersalesLogs.query.\
                filter(AftersalesLogs.aftersales_id == aftersales.aftersales_id).\
                order_by(AftersalesLogs.al_id.desc()).all()

    return render_template('mobile/aftersales/track.html.j2', logs=logs)


@aftersales.route('/apply')
def apply():
    """手机站 - 申请售后"""

    session['uid'] = 1
    session['uuid'] = 'edad8468-fb1a-4213-ae98-c45330dec77d'

    if not check_login():
        session['weixin_login_url'] = request.headers['Referer']
        return redirect(url_for('api.weixin.login'))
    uid = get_uid()

    order_id = toint(request.args.get('order_id', '0'))
    og_id    = toint(request.args.get('og_id', '0'))

    if order_id <= 0 and og_id <= 0:
        return redirect(request.headers['Referer'])

    ascs = AfterSalesCreateService(uid, order_id=order_id, og_id=og_id, quantity=1, aftersales_type=1, deliver_status=1)
    if order_id > 0:
        ret = ascs._check_order()
    else:
        ret = ascs._check_order_goods()

    if not ret:
        return redirect(request.headers['Referer'])

    wtf_form = AfterSalesForm()

    data = {'wtf_form':wtf_form, 'order_id':order_id, 'goods_data':ascs.goods_data, 'refunds_amount':ascs.refunds_amount}

    if order_id > 0:
        return render_template('mobile/aftersales/apply_order.html.j2', **data)
    else:
        return render_template('mobile/aftersales/apply.html.j2', **data)
