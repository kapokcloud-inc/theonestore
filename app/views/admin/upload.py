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


upload = Blueprint('admin.upload', __name__)

resjson = ResponseJson()
resjson.module_code = 22

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
        with open(config_filename) as fp:
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
