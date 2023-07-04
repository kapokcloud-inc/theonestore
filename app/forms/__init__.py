# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
# from wtforms.compat import iteritems
# from wtforms.fields import Field

from app.helpers import log_debug

class Form(FlaskForm):
    """
    表单基类
    """

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

    def fill_form(self, obj=None, data=None, **kwargs):
        """填充表单"""
        if data is not None:
            # XXX we want to eventually process 'data' as a new entity.
            #     Temporarily, this can simply be merged with kwargs.
            kwargs = dict(data, **kwargs)

        for name, field, in self._fields:
            if obj is not None and hasattr(obj, name):
                field.data = getattr(obj, name)
            elif name in kwargs:
                field.data = kwargs[name]

    
    def validate_on_submit(self):
        """表单校验"""
        primary_key = request.form.get('primary_key', '').strip()
        ret = super(Form, self).validate_on_submit()
        if ret is True or (not primary_key or primary_key == '0'):
            return ret

        # 编辑更新时文件上传是必填项报错问题
        for name, field, in self._fields:
            if (isinstance(field, FileField) is True
                    and field.flags.required
                    and not field.data
                    and field.errors):
                field.errors = ()
        
        for name, field in self._fields:
            if field.errors:
                return False

        return True

