# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import os
import gettext
import logging
import logging.config
import string

from flask import (
    Flask,
    current_app,
    request,
    render_template as flask_render_template,
)
from flask_uploads import (
    UploadSet, 
    configure_uploads as flask_configure_uploads, 
    DEFAULTS,
    patch_request_class
)


def create_app(config='config/config.cfg', default_app_name='app'):
    """创建app
    @param config 配置文件路径
    @param default_app_name 默认App名称
    """
    app = Flask(default_app_name)
    
    # config
    if config:
        app.config.from_pyfile(config)

    return app


def enable_logging(app, log_config="config/logging.ini"):
    """打开日志记录
    @param app Flask app对象
    @param log_config 日志配置文件，相对于当前app的相对路径，默认是config/logging.ini文件
    """
    if not log_config:
        return
    
    log_config = os.path.join(app.root_path, log_config)
    if os.path.isfile(log_config):
        logging.config.fileConfig(log_config)


def configure_uploads(app):
    """配置上传"""
    UPLOADED_FILES_DEST = app.config.get('UPLOADED_FILES_DEST', 'uploads')
    if UPLOADED_FILES_DEST[0] != '/':
        UPLOADED_FILES_DEST = os.path.join(os.getcwd(), 'uploads')
    
    print('UPLOADED_FILES_DEST:%s' % UPLOADED_FILES_DEST)
    app.config['UPLOADED_FILES_DEST'] = UPLOADED_FILES_DEST
    
    # default = UploadSet('default', DEFAULTS)
    # flask_configure_uploads(app, default)
    # 最大上传文件大小64M，MAX_CONTENT_LENGTH=64*1024*1024
    patch_request_class(app)


def log_info(logtext):
    extra_log = {'clientip':request.remote_addr}
    logger = logging.getLogger('web.info')
    logger.info(logtext, extra=extra_log)


def log_error(logtext):
    extra_log = {'clientip':request.remote_addr}
    logger = logging.getLogger('web.error')
    logger.error(logtext, extra=extra_log)


def log_debug(logtext):
    if current_app.config.get('DEBUG', False):
        extra_log = {'clientip':request.remote_addr}
        logger = logging.getLogger('web.debug')
        logger.debug(logtext, extra=extra_log)
    

def register_blueprint(app, modules):
    """注册Blueprint"""
    if modules:
        for module, url_prefix in modules:
            app.register_blueprint(module, url_prefix=url_prefix)


def render_template(template_name, **context):
    """渲染模板"""
    default_theme_name = current_app.config.get('DEFAULT_THEME_NAME', 'default')
    new_tpl_file = default_theme_name if template_name[0] == '/' else default_theme_name+'/'
    new_tpl_file += template_name
    return flask_render_template(new_tpl_file, **context)


def toint(s, base=10):
    """
    字符串转换成整型，对于不能转换的返回0
    :param s: 需要转换的字符串
    :param base: 多少进制，默认是10进制。如果是16进制，可以写0x或者0X
    :return: int
    """
    ns = u'%s' % s
    if ns.find('.') != -1:
        try:
            return int(string.atof(ns))
        except ValueError:
            #忽略错误
            pass
    else:
        try:
            return string.atoi(ns, base)
        except ValueError:
            #忽略错误
            pass

    return 0


def tofloat(s):
    """
    字符串转换成浮点型, 对于不能转换的返回float(0)
    :param s: 需要转换的字符串
    :return: float
    """
    try:
        return string.atof(s)
    except ValueError:
        pass

    return float(0)


def tolong(s):
    try:
        return string.atol(s)
    except ValueError:
        pass

    return long(0)