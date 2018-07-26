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
from app.helpers.date_time import current_timestamp

from app.forms.admin.adv import AdvForm

from app.models.adv import Adv


adv = Blueprint('admin.adv', __name__)

@adv.route('/index')
@adv.route('/index/<int:page>')
@adv.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """广告列表"""
    g.page_title = _(u'广告')

    args       = request.args
    tab_status = toint(args.get('tab_status', '0'))

    q = Adv.query

    if tab_status == 1:
        q = q.filter(Adv.ac_id == 1)

    advs       = q.order_by(Adv.adv_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/adv/index.html.j2', pagination=pagination, advs=advs)


@adv.route('/create')
def create():
    """添加广告"""
    g.page_title = _(u'添加广告')

    wtf_form = AdvForm()

    return render_template('admin/adv/detail.html.j2', wtf_form=wtf_form, adv={})


@adv.route('/detail/<int:adv_id>')
def detail(adv_id):
    """广告详情"""
    g.page_title = _(u'广告详情')

    adv = Adv.query.get_or_404(adv_id)

    wtf_form               = AdvForm()
    wtf_form.ac_id.data    = adv.ac_id
    wtf_form.ttype.data    = adv.ttype
    wtf_form.is_show.data  = adv.is_show

    return render_template('admin/adv/detail.html.j2', wtf_form=wtf_form, adv=adv)


@adv.route('/save', methods=['POST'])
def save():
    """保存广告"""
    g.page_title = _(u'保存广告')

    wtf_form     = AdvForm()
    current_time = current_timestamp()

    if wtf_form.validate_on_submit():
        adv_id = wtf_form.adv_id.data
        if adv_id:
            adv = Adv.query.get_or_404(adv_id)
        else:
            adv          = Adv()
            adv.add_time = current_time
            db.session.add(adv)

        adv.ac_id   = wtf_form.ac_id.data
        adv.desc    = wtf_form.desc.data
        adv.ttype   = wtf_form.ttype.data
        adv.tid     = wtf_form.tid.data
        adv.sorting = wtf_form.sorting.data
        adv.is_show = wtf_form.is_show.data
        db.session.commit()

        return redirect(url_for('admin.adv.index'))

    adv = wtf_form.data

    return render_template('admin/adv/detail.html.j2', wtf_form=wtf_form, adv=adv)


@adv.route('/remove/<int:adv_id>')
def remove(adv_id):
    """删除广告"""
    adv = Adv.query.get_or_404(adv_id)
    db.session.delete(adv)
    db.session.commit()

    return redirect(request.headers['Referer'])
