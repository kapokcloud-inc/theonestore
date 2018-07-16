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

from app.services.api.aftersales import AfterSalesCreateService

from app.forms.api.aftersales import AfterSalesForm


aftersales = Blueprint('mobile.aftersales', __name__)

@aftersales.route('/')
def root():
    """手机站 - 售后服务列表"""
    return render_template('mobile/aftersales/index.html.j2')


@aftersales.route('/<int:afs_id>')
def detail(afs_id):
    """手机站 - 售后服务详情"""
    return render_template('mobile/aftersales/detail.html.j2')


@aftersales.route('/track/<int:afs_id>')
def track(afs_id):
    """手机站 - 售后服务流水跟踪"""
    return render_template('mobile/aftersales/track.html.j2')


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

    ascs = AfterSalesCreateService(uid, order_id=order_id, og_id=og_id, quantity=1)
    if order_id > 0:
        ret = ascs._check_order()
    else:
        ret = ascs._check_order_goods()

    if not ret:
        return redirect(request.headers['Referer'])

    wtf_form = AfterSalesForm()

    data = {'wtf_form':wtf_form, 'order_id':order_id, 'goods_data':ascs.goods_data,
            'refunds_amount':ascs.refunds_amount, 'maximum':ascs.maximum}

    if order_id > 0:
        return render_template('mobile/aftersales/apply_order.html.j2', **data)
    else:
        return render_template('mobile/aftersales/apply.html.j2', **data)
