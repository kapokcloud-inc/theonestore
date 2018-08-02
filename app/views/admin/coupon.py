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
from sqlalchemy import (
    and_, or_, func
)
from werkzeug.datastructures import CombinedMultiDict
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db
from app.helpers import (
    render_template, 
    log_info,
    toint,
    model_create,
    model_update
)
from app.helpers.date_time import (
    current_timestamp,
    timestamp2str,
    str2timestamp
)
from app.forms.admin.coupon import CouponBatchForm
from app.models.coupon import (
    Coupon,
    CouponBatch
)


coupon = Blueprint('admin.coupon', __name__)

@coupon.route('/index')
@coupon.route('/index/<int:page>')
@coupon.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """优惠券列表"""
    g.page_title = _(u'优惠券')

    args         = request.args
    tab_status   = toint(args.get('tab_status', '0'))
    cb_name      = args.get('cb_name', '').strip()
    current_time = current_timestamp()

    q = CouponBatch.query

    if tab_status == 1:
        q = q.filter(CouponBatch.is_valid == 1).\
                filter(or_(CouponBatch.begin_time == 0, CouponBatch.begin_time <= current_time)).\
                filter(or_(CouponBatch.end_time == 0, CouponBatch.end_time >= current_time))
    elif tab_status == 2:
        q = q.filter(and_(CouponBatch.end_time > 0, CouponBatch.end_time < current_time))

    if cb_name:
        q = q.filter(CouponBatch.cb_name.like('%%%s%%' % cb_name))

    batches    = q.order_by(CouponBatch.cb_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/coupon/index.html.j2', pagination=pagination, batches=batches)


@coupon.route('/create')
def create():
    """添加优惠券"""
    g.page_title = _(u'添加优惠券')

    form = CouponBatchForm()

    return render_template('admin/coupon/detail.html.j2', form=form)


@coupon.route('/detail/<int:cb_id>')
def detail(cb_id):
    """优惠券详情"""
    g.page_title = _(u'优惠券详情')

    batch = CouponBatch.query.get_or_404(cb_id)

    batch.begin_time = timestamp2str(batch.begin_time, 'YYYY-MM-DD') if batch.begin_time else ''
    batch.end_time   = timestamp2str(batch.end_time, 'YYYY-MM-DD') if batch.end_time else ''

    form = CouponBatchForm()
    form.fill_form(batch)

    return render_template('admin/coupon/detail.html.j2', form=form)


@coupon.route('/save', methods=['POST'])
def save():
    """保存优惠券"""
    g.page_title = _(u'保存优惠券')

    form         = CouponBatchForm(CombinedMultiDict((request.files, request.form)))
    current_time = current_timestamp()

    if not form.validate_on_submit():
        return render_template('admin/coupon/detail.html.j2', form=form)

    cb_id = toint(form.cb_id.data)
    if cb_id:
        batch = CouponBatch.query.get_or_404(cb_id)
    else:
        batch = model_create(CouponBatch, {'add_time':current_time})

    begin_time = str2timestamp(form.begin_time.data, 'YYYY-MM-DD') if form.begin_time.data else 0
    end_time   = str2timestamp(form.end_time.data, 'YYYY-MM-DD') if form.end_time.data else 0
    data = {'cb_name':form.cb_name.data, 'begin_time':begin_time,
            'end_time':end_time, 'coupon_name':form.coupon_name.data,
            'is_valid':form.is_valid.data, 'publish_num':form.publish_num.data,
            'limit_amount':form.limit_amount.data, 'coupon_amount':form.coupon_amount.data,
            'date_num':form.date_num.data, 'coupon_from':form.coupon_from.data,
            'update_time':current_time}
    model_update(batch, data, commit=True)

    return redirect(url_for('admin.coupon.index'))


@coupon.route('/coupons')
@coupon.route('/coupons/<int:page>')
@coupon.route('/coupons/<int:page>-<int:page_size>')
def coupons(page=1, page_size=20):
    """用户优惠券列表"""
    g.page_title = _(u'用户优惠券')

    cb_id = toint(request.args.get('cb_id', '0'))

    q = Coupon.query

    if cb_id == 1:
        q = q.filter(Coupon.cb_id == cb_id)

    coupons    = q.order_by(Coupon.coupon_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/coupon/coupons.html.j2', pagination=pagination, coupons=coupons)

