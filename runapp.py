# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask_babel import Babel

from app.database import db

from app.helpers import (
    create_app, 
    enable_logging,
    register_blueprint
)
from app.helpers.date_time import timestamp2str

from app.routes import ROOT_ROUTES
from app.routes.admin import ADMIN_ROUTES
from app.routes.mobile import MOBILE_ROUTES


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
register_blueprint(app, MOBILE_ROUTES)

db.init_app(app)

app.jinja_env.auto_reload = True
jinja_filters             = {
    'timestamp2str':timestamp2str
}
app.jinja_env.filters.update(jinja_filters)

if __name__ == '__main__':
    app.config.from_pyfile('config/config.dev.cfg')
    babel.init_app(app)
    app.run(host='127.0.0.1', debug=True, port=5000)

