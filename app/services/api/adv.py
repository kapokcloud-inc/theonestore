# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask_babel import gettext as _

from app.database import db

from app.helpers import (
    log_info,
    toint
)

from app.models.adv import Adv


class AdvStaticMethodsService(object):
    """广告静态方法Service"""

    @staticmethod
    def advs(params, platform_type=1):
        """获取广告列表"""

        p   = toint(params.get('p', '1'))
        ps  = toint(params.get('ps', '10'))
        ac_id = toint(params.get('ac_id', '0'))

        advs = db.session.query(Adv.adv_id, Adv.ac_id, Adv.img, Adv.ttype, Adv.tid, Adv.url).\
                    filter(Adv.is_show == 1).\
                    filter(Adv.ac_id == ac_id).\
                    filter(Adv.platform_type == platform_type).\
                    order_by(Adv.sorting.desc()).\
                    order_by(Adv.adv_id.desc()).offset((p-1)*ps).limit(ps).all()

        return advs
