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
    make_response,
    Blueprint,
    g,
    redirect,
    url_for
)

from app.helpers import render_template


dashboard = Blueprint('admin_dashboard', __name__)


@dashboard.route('/', methods=['GET', 'POST'])
def index():
    """dashboard页"""
    return render_template('admin/dashboard/index.html.j2')
    
