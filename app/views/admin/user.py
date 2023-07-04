# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for,
    g
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db
from app.helpers import (
    render_template,
    log_info,
    toint,
    log_error,
    model_update,
    model_create
)
from app.helpers.date_time import (
    date_range,
    current_timestamp,
    some_day_timestamp
)

from app.models.funds import Funds, FundsDetail
from app.models.user import User
from app.models.coupon import Coupon, CouponBatch
from app.forms.admin.user import (
        RechargeForm,
        CouponForm
)

from app.services.api.funds import FundsService


user = Blueprint('admin_user', __name__)

@user.route('/index')
@user.route('/index/<int:page>')
@user.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """用户列表"""
    g.page_title = _(u'用户')

    args               = request.args
    nickname           = args.get('nickname', '').strip()
    add_time_daterange = args.get('add_time_daterange', '').strip()

    q = User.query

    if nickname:
        q = q.filter(User.nickname.like('%%%s%%' % nickname))

    if add_time_daterange:
        start, end = date_range(add_time_daterange)
        q          = q.filter(User.add_time >= start).filter(User.add_time < end)

    users      = q.order_by(User.uid.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/user/index.html.j2', pagination=pagination, users=users)


@user.route('/detail/')
@user.route('/detail/<int:page>')
@user.route('/detail/<int:page>-<int:page_size>')
def detail(page=1, page_size=20):
    """用户详情"""
    g.page_title = _(u'用户详情')

    uid   = toint(request.args.get('uid', '0'))
    user  = User.query.get_or_404(uid)
    funds = Funds.query.filter(Funds.uid == uid).first()
    
    q             = FundsDetail.query.filter(FundsDetail.uid == uid)
    funds_details = q.order_by(FundsDetail.fd_id.desc()).offset((page-1)*page_size).limit(page_size).all()

    pagination    = Pagination(None, page, page_size, 20, None)
    return render_template('admin/user/detail.html.j2', pagination=pagination, user=user, funds=funds, funds_details=funds_details)

@user.route('/recharge/<int:uid>')
def recharge(uid):
    """余额充值"""
    g.page_title = _(u'余额充值')
    
    user   = User.query.get_or_404(uid)

    form   = RechargeForm()
    form.fill_form(user)

    return render_template('admin/user/recharge.html.j2', form=form, uid=uid)


@user.route('/recharge/save', methods=['POST'])
def recharge_save():
    """充值"""

    admin_uid        = session.get('admin_uid', None)
    if not admin_uid: 
        return_url   = request.args.get('return_url', '/admin/dashboard')
        return redirect(url_for('admin_auth.login', return_url=return_url))
        
    form             = RechargeForm(request.form)
    form.avatar.data = request.args.get('avatar')
  
    if not form.validate_on_submit():
        return render_template('admin/user/recharge.html.j2', form=form)

    recharge_amount  = Decimal(form.recharge_amount.data).quantize(Decimal('0.00'))
    remark_user      = _(u'充值成功')
    remark_sys       = _(u'充值: 订单ID:%s, 充值方式:%s, 充值金额:%s' %(u"无", u"管理员打款", recharge_amount))
    fs               = FundsService(form.uid.data, recharge_amount, 1, 2, 0, remark_user, remark_sys, current_timestamp())
    if not fs.check():
        log_error('[ErrorServiceApiOrderPaidServicePaid][FundsServiceError01]  remark_sys:%s' % remark_sys)
        return redirect(url_for('admin_user.recharge', form=form))
    # 更新余额 - 充值
    fs.update()
    fs.commit()

    return redirect(url_for('admin_user.detail', uid=form.uid.data))


@user.route('/coupon/<int:uid>')
def coupon(uid):
    """优惠券派发"""
    g.page_title = _(u'优惠券派发')

    user   = User.query.get_or_404(uid)

    form   = CouponForm()
    form.fill_form(user)

    return render_template('admin/user/coupon.html.j2', form=form, user=user)

@user.route('/coupon/save', methods=['POST'])
def coupon_save():
    """优惠券派发保存"""

    admin_uid        = session.get('admin_uid', None)
    if not admin_uid: 
        return_url   = request.args.get('return_url', '/admin/dashboard')
        return redirect(url_for('admin_auth.login', return_url=return_url))
        
    form             = CouponForm(request.form)
    form.avatar.data = request.args.get('avatar')
  
    if not form.validate_on_submit():
        return render_template('admin/user/coupon.html.j2', form=form)

    coupon_batch = CouponBatch.query.filter(CouponBatch.cb_id == form.cb_id.data).first()

    if not coupon_batch:
        return render_template('admin/user/coupon.html.j2', form=form)

    #刷新优惠券数据
    give_num = coupon_batch.give_num + 1 
    data     = {'give_num':give_num}
    model_update(coupon_batch, data)


    coupon   = model_create(Coupon,{'add_time': current_timestamp()})

    data     = {'uid':form.uid.data, 'cb_id':coupon_batch.cb_id, 'coupon_name':coupon_batch.coupon_name,
                'begin_time':coupon_batch.begin_time, 'end_time':coupon_batch.end_time, 'is_valid':coupon_batch.is_valid,
                'limit_amount':coupon_batch.limit_amount, 'coupon_amount':coupon_batch.coupon_amount, 'limit_goods':coupon_batch.limit_goods, 'limit_goods_name':coupon_batch.limit_goods_name,
                'coupon_from':coupon_batch.coupon_from, 'update_timne':current_timestamp() }
    
    model_update(coupon, data, True)

    return redirect(url_for('admin_user.detail', uid=form.uid.data))