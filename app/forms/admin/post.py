# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
from flask_wtf import FlaskForm

from wtforms import (
    IntegerField,
    StringField,
    DecimalField,
    SelectField,
    TextAreaField,
    HiddenField,
    BooleanField
)

from wtforms.validators import (
    Required,
    InputRequired,
    Length,
    EqualTo,
    NumberRange
)

from app.database import db

from app.forms import Form

from app.models.post import (
    PostCategories,
    Post
)

class CategoryForm(Form):
    """分类form"""
    cat_id       = HiddenField(default=0)

    cat_name     = StringField(
                    _(u'分类名称'),
                    render_kw={'placeholder':_(u'请输入分类名称')},
                    validators=[
                        Required(message=_(u'必填项'))
                    ]
                )
    is_show      = BooleanField(_(u'是否显示'), false_values=(0, '0', ''), default=1)

class PostForm(Form):
    """文章form"""
    post_id       = HiddenField(default=0)

    cat_id        = SelectField(
                        _(u'分类'),
                        coerce=int,
                        validators=[
                            Required(message=_(u'请选择文章分类'))
                        ]
                    )

    post_name     = StringField(
                        _(u'文章名称'),
                        validators=[
                            Required(message=_(u'请填写文章名称'))
                        ]
                    )

    is_publish        = BooleanField(_(u'是否发布'), false_values=(0, '0', ''))

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        _categories = db.session.query(PostCategories.cat_id, PostCategories.cat_name).all()
        _categories = [(category.cat_id, category.cat_name) for category in _categories]
        self.cat_id.choices = _categories
    


class PostH5Form(FlaskForm):
    """文章H5form"""
    post_id = IntegerField()