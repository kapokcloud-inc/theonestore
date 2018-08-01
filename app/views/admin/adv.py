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
from werkzeug.datastructures import CombinedMultiDict

from app.database import db
from app.helpers import (
    render_template,
    log_info,
    toint,
    model_create,
    model_update,
    model_delete
)
from app.helpers.date_time import current_timestamp

from app.forms.admin.adv import AdvForm

from app.services.response import ResponseJson
from app.services.uploads import FileUploadService

from app.models.adv import Adv


adv = Blueprint('admin.adv', __name__)

resjson = ResponseJson()
resjson.module_code = 16

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

    form = AdvForm()

    return render_template('admin/adv/detail.html.j2', form=form)


@adv.route('/detail/<int:adv_id>')
def detail(adv_id):
    """广告详情"""
    g.page_title = _(u'广告详情')

    adv  = Adv.query.get_or_404(adv_id)
    form = AdvForm()
    form.fill_form(adv)

    return render_template('admin/adv/detail.html.j2', form=form)


@adv.route('/save', methods=['POST'])
def save():
    """保存广告"""
    g.page_title = _(u'保存广告')

    form         = AdvForm(CombinedMultiDict((request.files, request.form)))
    current_time = current_timestamp()

    if not form.validate_on_submit():
        return render_template('admin/adv/detail.html.j2', form=form)

    img = ''
    if form.img.data:
        fus = FileUploadService()
        try:
            img = fus.save_storage(form.img.data, 'adv')
        except Exception as e:
            form.img.errors = (_(u'上传失败，请检查云存储配置'))
            return render_template('admin/adv/detail.html.j2', form=form)

    adv_id = toint(form.adv_id.data)
    if adv_id:
        adv = Adv.query.get_or_404(adv_id)
    else:
        adv = model_create(Adv, {'add_time':current_time})

    img = img if img else adv.img
    data = {'ac_id':form.ac_id.data, 'img':img, 'desc':form.desc.data,
            'ttype':form.ttype.data, 'tid':form.tid.data, 'url':form.url.data,
            'sorting':form.sorting.data, 'is_show':form.is_show.data}
    model_update(adv, data, commit=True)

    return redirect(url_for('admin.adv.index'))


@adv.route('/remove')
def remove():
    """删除广告"""
    resjson.action_code = 10

    adv_id = toint(request.args.get('adv_id', '0'))

    if adv_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    adv = Adv.query.get(adv_id)
    if not adv:
        return resjson.print_json(10, _(u'广告不存在'))

    model_delete(adv, commit=True)

    return resjson.print_json(0, u'ok')
