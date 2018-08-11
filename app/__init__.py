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
    abort,
    g
)

from app.database import db

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

        # pc
        if endpoint.find('pc.') == 0:
            from app.models.item import GoodsCategories

            # nav推荐分类列表
            categories = db.session.query(GoodsCategories.cat_id, GoodsCategories.cat_name).\
                                filter(GoodsCategories.is_recommend == 1).\
                                order_by(GoodsCategories.sorting.desc()).\
                                order_by(GoodsCategories.cat_id.desc()).all()
            g.pc_nav_categories = categories

        if (endpoint.find('pc.') == 0) or (endpoint.find('mobile.') == 0):
            from app.helpers import get_count
            from app.models.user import UserLastTime
            from app.models.message import Message

            uid            = session.get('uid', 0)
            g.unread_count = 0

            if uid:
                # 未读消息
                ult            = UserLastTime.query.\
                                    filter(UserLastTime.uid == uid).\
                                    filter(UserLastTime.last_type == 1).first()
                last_time      = ult.last_time if ult else 0
                unread_count   = get_count(db.session.query(Message.message_id).\
                                    filter(Message.tuid == uid).\
                                    filter(Message.add_time > last_time))
                g.unread_count = unread_count

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
