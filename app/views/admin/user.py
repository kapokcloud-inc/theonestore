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
    url_for,
    g
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination

from app.database import db
from app.helpers import (
    render_template,
    log_info,
    toint
)
from app.helpers.date_time import date_range

from app.models.funds import Funds, FundsDetail
from app.models.user import User


user = Blueprint('admin.user', __name__)

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
    pagination    = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/user/detail.html.j2', pagination=pagination, user=user, funds=funds, funds_details=funds_details)
