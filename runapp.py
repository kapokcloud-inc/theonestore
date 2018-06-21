# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from wtforms.compat import iteritems

from app.database import db

from app.helpers import (
    create_app, 
    enable_logging,
    register_blueprint,
    configure_uploads,
    is_required
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

# 数据库初始化
db.init_app(app)

# 上传文件存储
configure_uploads(app)

# 启动form表单csr保护
CSRFProtect(app)

# 注册jinja模板过滤器
jinja_filters = {
    'iteritems':iteritems,
    'timestamp2str':timestamp2str,
    'is_required':is_required
}
app.jinja_env.filters.update(jinja_filters)


if __name__ == '__main__':
    app.config.from_pyfile('config/config.dev.cfg')
    babel.init_app(app)
    app.jinja_env.auto_reload = True
    app.run(host='127.0.0.1', debug=True, port=5000)

