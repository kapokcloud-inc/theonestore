# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.helpers import (
    create_app, 
    enable_logging,
    register_blueprint
)
from app.routes import ROOT_ROUTES

app = create_app()
enable_logging(app)
register_blueprint(app, ROOT_ROUTES)

if __name__ == '__main__':
    app.config.from_pyfile('app/config/config.dev.cfg')
    app.run(host='127.0.0.1', debug=True, port=1105)

