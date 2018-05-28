# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import Babel

from app.helpers import (
    create_app, 
    enable_logging,
    register_blueprint
)
from app.routes import ROOT_ROUTES
from app.routes.admin import ADMIN_ROUTES
from app.database import db

# 创建App
app = create_app()

# 打开日志记录
enable_logging(app)

# 多国语言i18n支持
babel = Babel()
babel.init_app(app)

# 注册路由
register_blueprint(app, ROOT_ROUTES)
register_blueprint(app, ADMIN_ROUTES)

db.init_app(app)

if __name__ == '__main__':
    app.config.from_pyfile('config/config.dev.cfg')
    babel.init_app(app)
    app.run(host='127.0.0.1', debug=True, port=1105)

