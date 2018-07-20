# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask_wtf import FlaskForm
from wtforms.compat import iteritems
from wtforms.fields import Field
from app.helpers import log_info

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

        for name, field, in iteritems(self._fields):
            if obj is not None and hasattr(obj, name):
                field.data = getattr(obj, name)
            elif name in kwargs:
                field.data = kwargs[name]
