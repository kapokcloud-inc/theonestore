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
    send_file
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (log_info,render_template)

from app.services.api.item import ItemStaticMethodsService
from app.services.api.adv import AdvStaticMethodsService

from app.models.adv import Adv


index = Blueprint('pc.index', __name__)


@index.route('/')
def root():
    """pc - 首页"""
    
    advs           = AdvStaticMethodsService.advs({'ac_id':1}, platform_type=2)
    data_hot       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    data_recommend = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})

    data = {'advs':advs, 'hot_items':data_hot['items'], 'recommend_items':data_recommend['items']}
    return render_template('pc/index/index.html.j2', **data)

@index.route('/favicon.ico')
def favicon():
    """favicon图标"""
    return send_file('static/favicon.ico')


@index.route('/404')
def pagenotfound():
    """页面未找到"""
    return render_template('pc/index/404.html.j2')


@index.route('/500')
def servererror():
    """服务器内部发生错误"""
    return render_template('pc/index/500.html.j2')
