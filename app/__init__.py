# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import (
    session, 
    request, 
    redirect, 
    url_for,
    abort
)

from app.helpers import (
    get_uuid, 
    render_template,
    log_info
)


def configure_before(app):
    @app.before_request
    def before_request():
        session_id = session.get('session_id', '')
        if not session_id:
            session['session_id'] = get_uuid()

        endpoint = request.endpoint
        if endpoint is None:
            return

        # 管理后台权限判断
        if (endpoint.find('admin.') == 0 and 
                (endpoint not in ('admin.index.root', 'admin.auth.login'))):
            admin_uid = session.get('admin_uid', 0)
            if admin_uid <= 0:
                return abort(403)

    @app.errorhandler(403)
    def forbidden(error):
        endpoint = request.endpoint
        if (endpoint and endpoint.find('admin.') == 0):
            if not request.is_xhr:
                return render_template('admin/403.html.j2')

    @app.errorhandler(404)
    def page_not_found(error):
        path = request.path
        if (path.find('/admin/') == 0 or path.find('/static/') == 0):
            if not request.is_xhr:
                return render_template('admin/404.html.j2')

    @app.errorhandler(500)
    def server_error(error):
        endpoint = request.endpoint
        if (endpoint.find('admin.') == 0):
            if not request.is_xhr:
                return render_template('admin/500.html.j2')
