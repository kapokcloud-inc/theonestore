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
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db
from app.helpers import (
    render_template, 
    log_info,
    toint
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

    wtf_form = CouponBatchForm()

    return render_template('admin/coupon/detail.html.j2', wtf_form=wtf_form, batch={})


@coupon.route('/detail/<int:cb_id>')
def detail(cb_id):
    """优惠券详情"""
    g.page_title = _(u'优惠券详情')

    batch = CouponBatch.query.get_or_404(cb_id)

    wtf_form               = CouponBatchForm()
    wtf_form.is_valid.data = batch.is_valid

    batch.begin_time = timestamp2str(batch.begin_time, 'YYYY-MM-DD') if batch.begin_time else ''
    batch.end_time   = timestamp2str(batch.end_time, 'YYYY-MM-DD') if batch.end_time else ''

    return render_template('admin/coupon/detail.html.j2', wtf_form=wtf_form, batch=batch)


@coupon.route('/save', methods=['POST'])
def save():
    """保存优惠券"""
    g.page_title = _(u'保存优惠券')

    wtf_form     = CouponBatchForm()
    current_time = current_timestamp()

    if wtf_form.validate_on_submit():
        cb_id = wtf_form.cb_id.data
        if cb_id:
            batch = CouponBatch.query.get_or_404(cb_id)
        else:
            batch          = CouponBatch()
            batch.add_time = current_time
            db.session.add(batch)

        batch.cb_name       = wtf_form.cb_name.data
        batch.begin_time    = str2timestamp(wtf_form.begin_time.data, 'YYYY-MM-DD') if wtf_form.begin_time.data else 0
        batch.end_time      = str2timestamp(wtf_form.end_time.data, 'YYYY-MM-DD') if wtf_form.end_time.data else 0
        batch.coupon_name   = wtf_form.coupon_name.data
        batch.is_valid      = wtf_form.is_valid.data
        batch.publish_num   = wtf_form.publish_num.data
        batch.limit_amount  = wtf_form.limit_amount.data
        batch.coupon_amount = wtf_form.coupon_amount.data
        batch.date_num      = wtf_form.date_num.data
        batch.coupon_from   = wtf_form.coupon_from.data
        batch.update_time   = current_time
        db.session.commit()

        return redirect(url_for('admin.coupon.index'))

    batch = wtf_form.data

    return render_template('admin/coupon/detail.html.j2', wtf_form=wtf_form, batch=batch)


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

