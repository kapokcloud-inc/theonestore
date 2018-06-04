# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

import arrow

from app.helpers import (
    log_info
)


def timestamp2str(timestamp, format_style='YYYY-MM-DD HH:mm:ss'):
    """时间戳转换为指定格式时间"""

    utc = arrow.get(timestamp)
    loc = utc.to('local')

    return loc.format(format_style)




