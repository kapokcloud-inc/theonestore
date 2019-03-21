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

from app.services.api.item import ItemListService
from app.services.api.adv import AdvStaticMethodsService

from app.models.adv import Adv


index = Blueprint('pc.index', __name__)


@index.route('/')
def root():
    """pc - 首页"""
    
    advs           = AdvStaticMethodsService.advs({'ac_id':1}, platform_type=2)

    # 热门商品列表
    hot_service = ItemListService(1, 12, is_hot=1)
    hot_items = hot_service.items()
    
    # 推荐商品列表
    recommend_service = ItemListService(1, 12, is_recommend=1)
    recommend_items = recommend_service.items()

    return render_template('pc/index/index.html.j2', 
                advs = advs,
                hot_items = hot_items,
                recommend_items = recommend_items
            )
            

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
