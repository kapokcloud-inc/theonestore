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

sys = Blueprint('admin.sys', __name__)

@sys.route('/setting')
def setting():
    """配置信息"""
    return render_template('admin/sys/setting.html.j2')
