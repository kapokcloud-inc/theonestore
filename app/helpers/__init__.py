# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import os
import logging
import logging.config

from flask import Flask


def create_app(config='app/config/config.cfg', default_app_name='theonestore'):
    """创建app
    @param config 配置文件路径
    @param default_app_name 默认App名称
    """
    app = Flask(default_app_name)
    
    # config
    if config:
        osname = os.name.upper()
        if osname == 'NT':
            config = config.replace('/', '\\')
        app.config.from_pyfile(config)

    return app


def enable_logging(app, log_config="app/config/logging.ini"):
    """打开日志记录
    @param app Flask app对象
    @param log_config 日志配置文件，相对于当前app的相对路径，默认是config/logging.ini文件
    """
    if not log_config:
        return

    osname = os.name.upper()
    if osname == 'NT':
        log_config = log_config.replace('/', '\\')
    
    log_config = os.path.join(app.root_path, log_config)
    if os.path.isfile(log_config):
        logging.config.fileConfig(log_config)
    

def register_blueprint(app, modules):
    """注册Blueprint"""
    if modules:
        for module, url_prefix in modules:
            app.register_blueprint(module, url_prefix=url_prefix)

