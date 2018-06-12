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


def str2timestamp(str, format_style='YYYY-MM-DD HH:mm:ss'):
    """指定格式时间转换为时间戳"""

    utc = arrow.get(str, format_style)
    loc = utc.to('local')

    return loc.timestamp


def current_timestamp():
    """当前时间戳"""

    return int(time.time())


def some_day_timestamp(timestamp, days):
    """获取某天0点00分00秒的时间戳"""

    a_utc = arrow.get(timestamp)
    a_loc = a_utc.to('local')
    a_loc = a_loc.floor('day')
    a_loc = a_loc.shift(days=days)

    return a_loc.timestamp


def before_after_timestamp(timestamp, **kwargs):
    """"""

    a_utc = arrow.get(timestamp)
    a_loc = a_utc.to('local')
    a_loc = a_loc.shift(**kwargs)

    return a_loc.timestamp


def date_range(_range, format_style='YYYY-MM-DD'):
    """时间段"""

    _range = _range.split(' - ')
    start  = str2timestamp(_range[0], format_style)
    end    = str2timestamp(_range[1], format_style)
    end    = some_day_timestamp(end, 1)

    return (start, end)




