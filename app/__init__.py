# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import request

from app.helpers import set_lang

def configure_before_handlers(app):

    @app.before_request
    def before_request():

        # 设置语言
        lang = request.args.get('lang', 'zh_CN')
        #set_lang(lang)