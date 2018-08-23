# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import json

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for,
    g,
    jsonify
)
from flask_babel import gettext as _
from flask_sqlalchemy import Pagination
from werkzeug.datastructures import CombinedMultiDict

from app.database import db

from app.helpers import (
    render_template, 
    log_info,
    toint,
    model_create,
    model_update,
    model_delete
)

from app.forms.admin.post import (
    CategoryForm,
    PostForm,
    PostH5Form
)

from app.helpers.date_time import current_timestamp

from app.models.post import (
    PostCategories,
    Post
)

from app.services.response import ResponseJson

post = Blueprint('admin.post', __name__)

resjson = ResponseJson()
resjson.module_code = 20

@post.route('/categories')
@post.route('/categories/<int:page>')
@post.route('/categories/<int:page>-<int:page_size>')
def categories(page=1, page_size=10):
    """分类列表"""
    g.page_title = _(u'分类')

    q = PostCategories.query
    
    categories = q.order_by(PostCategories.cat_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    return render_template('admin/post/categories.html.j2', pagination=pagination, categories=categories)


@post.route('/category/create')
def category_create():
    """添加分类"""
    g.page_title = _(u'添加分类')

    form = CategoryForm()

    return render_template('admin/post/category_detail.html.j2', form=form)

@post.route('/category/detail/<int:cat_id>')
def category_detail(cat_id):
    """分类详情"""
    g.page_title = _(u'分类详情')

    category = PostCategories.query.get_or_404(cat_id)
    form = CategoryForm()
    form.fill_form(category)

    return render_template('admin/post/category_detail.html.j2', form=form)


@post.route('/category/save', methods=['POST'])
def category_save():
    """保存分类"""
    g.page_title = _(u'保存分类')

    form = CategoryForm(CombinedMultiDict((request.files, request.form)))

    if not form.validate_on_submit():
        return render_template('admin/post/category_detail.html.j2', form=form)

    cat_id = toint(form.cat_id.data)
    if cat_id:
        category = PostCategories.query.get_or_404(cat_id)
    else:
        category = model_create(PostCategories, {'add_time':current_timestamp()})

    data    = {'cat_name':form.cat_name.data, 'is_show':form.is_show.data}
    model_update(category, data, commit=True)

    return redirect(url_for('admin.post.categories'))

@post.route('/category/remove')
def category_remove():
    """删除分类"""
    resjson.action_code = 12

    cat_id = toint(request.args.get('cat_id', '0'))

    if cat_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    category = PostCategories.query.get(cat_id)
    if not category:
        return resjson.print_json(10, _(u'分类不存在'))

    item = Post.query.filter(Post.cat_id == cat_id).all()
    if item:
        return resjson.print_json(11, _(u'分类下有文章，禁止删除！'))

    model_delete(category, commit=True)

    return resjson.print_json(0, u'ok')

@post.route('/index')
@post.route('/index/<int:page>')
@post.route('/index/<int:page>-<int:page_size>')
def index(page=1, page_size=20):
    """文章列表"""
    g.page_title = _(u'文章')

    args       = request.args
    tab_status = toint(args.get('tab_status', '0'))
    cat_id     = toint(args.get('cat_id', '0'))
    post_name = args.get('post_name', '').strip()

    q = db.session.query(Post.post_id, Post.post_name, Post.post_detail , 
                            Post.is_publish, Post.cat_id, Post.cat_name, 
                            Post.add_time, Post.update_time).\
                        filter(Post.cat_id == PostCategories.cat_id)

    if cat_id > 0:
        q = q.filter(Post.cat_id == cat_id)
    
    if tab_status == 1:
        q = q.filter(Post.is_publish == 1)
    
    if tab_status == 2:
        q = q.filter(Post.is_publish == 0)

    if post_name:
        q = q.filter(Post.post_name.like('%%%s%%' % post_name))
    
    items      = q.order_by(Post.post_id.desc()).offset((page-1)*page_size).limit(page_size).all()
    pagination = Pagination(None, page, page_size, q.count(), None)

    cats  = [{'name':_(u'请选择……'), 'value':'-1'}]
    _cats = db.session.query(PostCategories.cat_id, PostCategories.cat_name).\
                order_by(PostCategories.cat_id.desc()).all()
    for _cat in _cats:
        cat = {'name':_cat.cat_name, 'value':_cat.cat_id}
        cats.append(cat)


    return render_template('admin/post/index.html.j2', pagination=pagination, items=items, cats=cats)


@post.route('/create')
def create():
    """添加文章"""
    g.page_title = _(u'添加文章')

    form = PostForm()

    return render_template('admin/post/detail.html.j2', form=form, item=None)


@post.route('/detail/<int:post_id>')
def detail(post_id):
    """文章详情"""
    g.page_title = _(u'文章详情')

    item = Post.query.get_or_404(post_id)
    form = PostForm()
    form.fill_form(item)

    return render_template('admin/post/detail.html.j2', form=form, item=item)

@post.route('/save', methods=['POST'])
def save():
    """保存文章"""
    g.page_title = _(u'保存文章')

    form         = PostForm(CombinedMultiDict((request.files, request.form)))
    current_time = current_timestamp()

    if not form.validate_on_submit():
        return render_template('admin/post/detail.html.j2', form=form, item=form.data)
        
    post_id = toint(form.post_id.data)
    if post_id:
        item = Post.query.get_or_404(post_id)
    else:
        item = model_create(Post, {'post_detail':'', 'add_time':current_time})

    cat_id   = form.cat_id.data
    data = db.session.query(PostCategories.cat_name).filter(PostCategories.cat_id==cat_id).first()

    data = {'cat_id':form.cat_id.data, 'cat_name':data[0], 'post_name':form.post_name.data, 'is_publish':form.is_publish.data, 'update_time':current_time}
    model_update(item, data, commit=True)

    return redirect(url_for('admin.post.h5', post_id=item.post_id))

    


@post.route('/remove')
def remove():
    """删除文章"""
    resjson.action_code = 10

    post_id = toint(request.args.get('post_id', '0'))

    if post_id <= 0:
        return resjson.print_json(resjson.PARAM_ERROR)

    item = Post.query.get(post_id)
    if not item:
        return resjson.print_json(10, _(u'文章不存在'))

    model_delete(item, commit=True)

    return resjson.print_json(0, u'ok')


@post.route('/h5/<int:post_id>')
def h5(post_id):
    """文章H5详情"""
    g.page_title = _(u'文章详情')

    item     = Post.query.get_or_404(post_id)
    wtf_form = PostH5Form()

    return render_template('admin/post/h5.html.j2', wtf_form=wtf_form, item=item)


@post.route('/h5/save', methods=['POST'])
def h5_save():
    """保存文章H5"""
    g.page_title = _(u'保存文章')

    post_id = toint(request.form.get('post_id', '0'))
    post_detail   = request.form.get('detail', '').strip()

    item = Post.query.get_or_404(post_id)
    item.post_detail = post_detail
    db.session.commit()

    return redirect(url_for('admin.post.index'))