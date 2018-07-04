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

from app.helpers import render_template


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
    return render_template('mobile/aftersales/apply.html.j2')
