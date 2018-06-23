# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import session

from app.helpers import get_uuid


def configure_before(app):
    @app.before_request
    def before_request():
        session_id = session.get('session_id', '')
        if not session_id:
            session['session_id'] = get_uuid()
