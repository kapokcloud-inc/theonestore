# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint


index = Blueprint('index', __name__)


@index.route('/hello')
def hello():
    """网站首页"""
    return "Hello,world!"
    