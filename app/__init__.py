# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import os
from flask_babel import gettext as _
from flask import (
    current_app,
    session, 
    request, 
    redirect, 
    url_for,
    abort,
    send_from_directory,
    g
)

from app.database import db
from app.services.response import ResponseJson
from app.helpers import (
    get_uuid, 
    render_template,
    log_info
)


def configure_before(app):
    @app.before_request
    def before_request():
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
            from app.services.api.user import UserStaticMethodsService

            uid = session.get('uid', 0)
            g.unread_count = 0

            if uid:
                # 未读消息数
                g.unread_count = UserStaticMethodsService.unread_count(uid)
        
        
        # PC待评价数
        if (endpoint.find('pc.order') == 0) or (endpoint.find('pc.aftersales') == 0) or (endpoint.find('pc.me')  == 0) or (endpoint.find('pc.wallet')  == 0):

            from app.models.order import (Order, OrderGoods)
            from app.helpers import get_count

            uid = session.get('uid', 0)
            g.uncomment_count = 0
            
            if uid:
                completed = db.session.query(Order.order_id).\
                                    filter(Order.uid == uid).\
                                    filter(Order.is_remove == 0).\
                                    filter(Order.order_status == 2).\
                                    filter(Order.pay_status == 2).\
                                    filter(Order.deliver_status == 2).all()
                completed = [order.order_id for order in completed]

                q         = db.session.query(OrderGoods.og_id).\
                                    filter(OrderGoods.order_id.in_(completed)).\
                                    filter(OrderGoods.comment_id == 0)

                g.uncomment_count = get_count(q)


    @app.errorhandler(403)
    def forbidden(error):
        endpoint = request.endpoint
        if (endpoint and endpoint.find('admin.') == 0):
            if not request.is_xhr:
                return render_template('admin/403.html.j2')

    @app.errorhandler(404)
    def page_not_found(error):
        path = request.path.lower()

        # api端或者是ajax请求
        if (path.find('/api/') == 0 or request.is_xhr):
            resjson = ResponseJson()
            return resjson.print_json(resjson.SYSTEM_PAGE_NOT_FOUND)

        # 手机端
        elif (path.find('/mobile/') == 0):
            return render_template('mobile/index/404.html.j2')
        elif (path.find('/admin/') == 0 or path.find('/static/') == 0):
            return render_template('admin/404.html.j2')

        # 微信公众号校验文件
        elif (path.find('/MP_verify_') == 0 and path[-4:] == '.txt'):
            filename = path[1:]
            uploads_path = current_app.config['UPLOADED_FILES_DEST']
            mp_verify_file = os.path.join(uploads_path, filename)
            if os.path.exists(mp_verify_file):
                return send_from_directory(uploads_path, filename)
            return _(u'文件找不到')

        # 微信退款证书
        elif (path.find('/apiclient_cert.pem') or path.find('/apiclient_key.pem')):
            admin_uid = session.get('admin_uid', None)
            if not admin_uid:
                return render_template('admin/404.html.j2')
            dirname = os.path.join(os.getcwd(), 'pem')
            filename = path[1:]
            pemfile = os.path.join(dirname, filename)
            if os.path.exists(pemfile):
                return send_from_directory(dirname, filename)
            return render_template('admin/404.html.j2')

        # pc页面
        return render_template('pc/index/404.html.j2')


    @app.errorhandler(500)
    def server_error(error):
        endpoint = request.endpoint
        if not request.is_xhr:
            if (endpoint.find('mobile.') == 0):
                return render_template('mobile/index/500.html.j2')
            elif (endpoint.find('pc.') == 0):
                return render_template('pc/index/500.html.j2')
            elif (endpoint.find('admin.') == 0):
                return render_template('admin/500.html.j2')

        resjson = ResponseJson()
        return resjson.print_json(resjson.SYSTEM_BUSY)

