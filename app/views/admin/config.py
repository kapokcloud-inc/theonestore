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
from app.database import db

config = Blueprint('admin.config', __name__)

@config.route('/sms/yunpian')
def sms_yunpian():
    """配置云片短信"""
    return render_template('admin/sys/sms_yunpian.html.j2')


@config.route('/sms/alisms')
def sms_alisms():
    """配置阿里短信"""
    return render_template('admin/sys/sms_alisms.html.j2')


@config.route('/storage/qiniu')
def storage_qiniu():
    """配置七牛存储"""
    return render_template('admin/sys/storage_qiniu.html.j2')


@config.route('/storage/alioss')
def storage_alioss():
    """配置七牛存储"""
    return render_template('admin/sys/storage_alioss.html.j2')
