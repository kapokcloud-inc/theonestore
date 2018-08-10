# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import os
import re
import json

from flask import (
    Blueprint,
    request,
    session,
    current_app,
    make_response
)
from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)
from app.helpers.date_time import current_timestamp
from app.helpers.user import check_login

from app.forms.api.upload import UploadImageForm

from app.services.response import ResponseJson
from app.services.uploads import FileUploadService


upload = Blueprint('api.upload', __name__)

resjson = ResponseJson()
resjson.module_code = 17

@upload.route('/image', methods=["POST"])
def image():
    """上传图片"""
    resjson.action_code = 10

    if not check_login():
        return resjson.print_json(10, _(u'未登陆'))

    wtf_form = UploadImageForm()
    if not wtf_form.validate_on_submit():
        for key,value in wtf_form.errors.items():
            msg = value[0]
        return resjson.print_json(10, msg)

    try:
        fus   = FileUploadService()
        image = fus.save_storage(wtf_form.image.data, wtf_form.prefix.data)
    except Exception as e:
        return resjson.print_json(10, _(u'上传失败，请检查云存储配置'))

    return resjson.print_json(0, u'ok', {'image':image})


@upload.route('/ueditor', methods=["GET", "POST"])
def ueditor():
    """ueditor上传"""
    res = current_app.response_class(mimetype='application/json')
    # res = make_response(mimetype='application/json')
    action = request.args.get('action')

    if action == 'config':
        # 解析JSON格式的配置文件
        # 这里使用PHP版本自带的config.json文件
        config_filename = os.path.join(current_app.static_folder, 'default', 'admin', 'plugins', 'ue', 'php', 'config.json')
        with open(config_filename, encoding='utf8') as fp:
            data = fp.read()
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', data))
            # log_info('##########:%s' % CONFIG)
            res.data = json.dumps(CONFIG)
        
        log_info('-----------------')
        return res

    # 获取上传文件
    upfile = request.files['upfile']

    try:
        fus   = FileUploadService()
        image = fus.save_storage(upfile, 'ueditor')
    except Exception as e:
        return json.dumps({'state':'FAIL'})

    data = {'state':'SUCCESS', 'source':image, 'url':image, 'title':image, 'original':image}
    res.data = json.dumps(data)
    return res
