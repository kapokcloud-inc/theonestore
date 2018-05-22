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
    render_template,
    make_response,
    Blueprint,
    g,
    redirect,
    url_for
)


auth = Blueprint('admin.auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登陆"""

    if request.method == 'GET':
        args     = request.args
        mobile   = args.get('mobile', '')
        password = args.get('password', '')

        return render_template('admin/default/auth/login.html.j2', f={}, errormsg={})

    form     = request.form
    mobile   = form.get('mobile', '')
    password = form.get('password', '')

    if mobile and password:
        return False

    return render_template('admin/default/auth/login.html.j2', f={}, errormsg={})