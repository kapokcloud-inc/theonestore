# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from flask import (
    request,
    session,
    Blueprint,
    redirect,
    url_for
)

from app.helpers import (
    render_template,
    log_info,
    toint,
    get_count
)

from app.services.api.post import PostStaticMethodsService

post = Blueprint('pc.post', __name__)

@post.route('/<int:post_id>')
def detail(post_id=0):
    """获取文章详情"""
    if post_id <= 0:
        return redirect(url_for('pc.index.pagenotfound'))

    post      = PostStaticMethodsService.post_detail(post_id)
    
    if not post:
        return redirect(url_for('pc.index.pagenotfound'))

    posts     = []
        #文章列表
    posts = PostStaticMethodsService.posts(post.cat_id)

    data      = {'post':post, 'posts':posts}
    
    return render_template('pc/post/detail.html.j2', **data)