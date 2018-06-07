# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import arrow
import time

from app.helpers import log_info


def timestamp2str(timestamp, format_style='YYYY-MM-DD HH:mm:ss'):
    """时间戳转换为指定格式时间"""

    utc = arrow.get(timestamp)
    loc = utc.to('local')       # 时区 ??

    return loc.format(format_style)


def current_time():
    """当前时间戳"""

    return int(time.time())




