# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import time
import os
import gettext
import logging
import logging.config
import string
import uuid
import urllib
import types
import random
import json
try:
    import urlparse
except Exception as e:
    from urllib.parse import urlparse
from decimal import Decimal

from flask import (
    Flask,
    current_app,
    request,
    render_template as flask_render_template,
)
from flask_uploads import (
    UploadSet, 
    configure_uploads as flask_configure_uploads,
    DOCUMENTS,
    IMAGES,
    TEXT
)
from flask_wtf.file import FileAllowed
from sqlalchemy import func

from app.database import db


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
    app.config['UPLOADED_FILES_DEST'] = UPLOADED_FILES_DEST
    app.config['UPLOADED_DOCUMENTS_DEST'] = os.path.join(UPLOADED_FILES_DEST, 'documents')
    app.config['UPLOADED_IMAGES_DEST'] = os.path.join(UPLOADED_FILES_DEST, 'images')
    app.config['UPLOADED_TEXT_DEST'] = os.path.join(UPLOADED_FILES_DEST, 'text')
    app.config['UPLOADED_PEM_DEST'] = os.path.join(UPLOADED_FILES_DEST, 'pem')

    documents = UploadSet('documents', DOCUMENTS)
    images = UploadSet('images', IMAGES)
    text = UploadSet('text', TEXT)
    pem = UploadSet('pem', ('pem',))
    flask_configure_uploads(app, (documents, images, text, pem))
    
    # 最大上传文件大小64M，MAX_CONTENT_LENGTH=64*1024*1024
    # patch_request_class(app)


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
            return int(float(ns))
        except ValueError:
            #忽略错误
            pass
    else:
        try:
            return int(ns, base)
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
        return float(s)
    except ValueError:
        pass

    return float(0)


def toamount(base):
    """转换成金额"""

    return Decimal(base).quantize(Decimal('0.00'))


def randomstr(random_len=6, random_type=0):
    """
    获取随机字符串
    @param random_len: 随机字符串长度
    @param random_type: 随机类型 0:大小写数字混合 1:数字 2:小写字母 3:大写字母
    @return string
    """
    random_str_lists = ['0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                        '0123456789',
                        'abcdefghijklmnopqrstuvwxyz',
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    if random_type < 0 or random_type > len(random_str_lists):
        random_type = 0

    random_string = random_str_lists[random_type]
    return ''.join(random.sample(random_string, random_len))


def urlencode(params):
    """url转码"""

    if not params:
        return ''

    _params = params.copy()
    for k,v in params.items():
        try:
            if isinstance(v, types.StringType) or isinstance(v, types.UnicodeType):
                _params[k] = v.encode('utf8')
        except Exception as e:
            if isinstance(v, str):
                _params[k] = v.encode('utf8')

    try:
        url = urllib.urlencode(_params)
    except Exception as e:
        url = urllib.parse.urlencode(params)

    return url


def url_push_query(url, key_value_str):
    """url增加query参数"""
    try:
        url_tuple = urlparse.urlparse(url)
    except Exception as e:
        url_tuple = urllib.parse.urlparse(url)

    query     = key_value_str if url_tuple.query == '' else url_tuple.query+'&'+key_value_str
    new_tuple = (url_tuple.scheme, url_tuple.netloc, url_tuple.path, url_tuple.params, query, url_tuple.fragment)

    try:
        url = urlparse.urlunparse(new_tuple)
    except Exception as e:
        url = urllib.parse.urlunparse(new_tuple)

    return url


def model_to_dict(model):
    """ orm model转换成dict """

    ret = {}
    for c in model.__table__.columns:
        ret[c.name] = getattr(model, c.name)

    return ret


def model_to_dict_only(model, only=[]):
    """ orm model转换成dict - only版 """

    __dict = model_to_dict(model)

    _dict = {}
    for key in only:
        _dict[key] = __dict.get(key, None)

    return _dict


def ml_to_dl(model_list):
    """ model list to dict list """

    return [model_to_dict(m) for m in model_list]


def kt_to_dict(kt):
    """KeyedTuple转换成Dict"""

    return kt._asdict()


def ktl_to_dl(kt_list):
    """ KeyedTuple List转换成Dict List """

    return [kt_to_dict(kt) for kt in kt_list]


def static_uri(uri):
    """静态文件uri"""
    debug = current_app.config['DEBUG']    
    if debug is True:
        if uri.find('?') != -1:
            uri += u'&'
        else:
            uri += u'?'
        
        uri += u'_=%d' % (int(time.time()),)

    log_debug('uri:%s'%uri)
    return uri

def get_uuid():
    """获取uuid"""

    return '%s' % uuid.uuid4()


def model_create(model, data, commit=False):
    """Model - 创建"""

    record = model(**data)
    db.session.add(record)

    if commit:
        db.session.commit()

    return record


def model_update(record, data, commit=False):
    """Model - 更新"""

    for attr, value in data.items():
        setattr(record, attr, value)

    if commit:
        db.session.commit()

    return record


def model_delete(record, commit=False):
    """Model - 删除"""

    db.session.delete(record)

    if commit:
        db.session.commit()


def get_count(q):
    # count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count_q = q.statement.with_only_columns(func.count()).order_by(None)
    count   = q.session.execute(count_q).scalar()

    return count


def randomstr(random_len = 6, random_type = 0):
    """
    获取随机字符串
    :param random_len: 随机字符串长度
    :param random_type: 随机类型 0:大小写数字混合 1:数字 2:小写字母 3:大写字母
    :return string
    """
    random_string_array = ['0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    if random_type < 0 or random_type > len(random_string_array):
        random_type = 0

    random_string = random_string_array[random_type]
    return ''.join(random.sample(random_string, random_len))


def get_file_uploadtype(field):
    """获取文件上传类型
    :param field
    :return string
    """
    uploadtype = ''
    for validator in field.validators:
        if isinstance(validator, FileAllowed):
            uploadtype = validator.upload_set.name
    return uploadtype


def request_args_to_query_string(params, p, ps):
    """分页url转换"""

    params['p']  = p
    params['ps'] = ps

    return urlencode(params)


def is_mobile_device(agent):
    """是否移动设备"""
    mobile_device_list = ('Android', 'iPhone', 'iPod', 'iPad')
    for device in mobile_device_list:
        if agent.find(device) != -1:
            return True
    return False
