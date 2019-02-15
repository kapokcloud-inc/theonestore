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
    Blueprint,
    json
)
from sqlalchemy import func
from flask_babel import gettext as _
from app.database import db
from app.helpers import (
    log_info
)
from app.helpers.data_format import format_array_data_to_dict
from app.helpers.date_time import (
    current_timestamp,
    date_range,
    timestamp2str,
    some_day_timestamp,
    date_cover_day
)
from app.services.api.item import ItemStaticMethodsService
from app.services.api.adv import AdvStaticMethodsService
from app.services.response import ResponseJson
from app.models.order import (
    Order
)

index = Blueprint('api.index', __name__)

resjson = ResponseJson()
resjson.module_code = 20

@index.route('/home')
def home():
    """首页"""
    resjson.action_code = 10
    
    advs           = AdvStaticMethodsService.advs({'ac_id':1}, platform_type=1)
    data_hot       = ItemStaticMethodsService.items({'is_hot':1, 'p':1, 'ps':12})
    data_recommend = ItemStaticMethodsService.items({'is_recommend':1, 'p':1, 'ps':12})

    data = {'advs':advs, 'hot_items':data_hot['items'], 'recommend_items':data_recommend['items']}
    return resjson.print_json(0, u'ok', data)

@index.route('/chartlist')
def chartlist():
    """ 销售趋势图表 """
    
    resjson.action_code = 11
    
    # 获取查询日期
    search_time_daterange = request.args.get('search_time_daterange', '').strip()
    
    q = db.session.query(func.count(Order.order_id).label('order_num'),
                            func.sum(Order.pay_amount).label('pay_amount'), 
                            func.from_unixtime(Order.paid_time, "%Y-%m-%d").label('paid_date')).\
                        filter(Order.order_type == 1).\
                        filter(Order.pay_status == 2)

    # 查询日期
    if search_time_daterange:
        temp_start, temp_end = date_range(search_time_daterange)
        _cover_day, _date_norms = date_cover_day(temp_start, temp_end)
        start = temp_start
        end   = temp_end
        date_norms = _date_norms
    else:
        return resjson.print_json(resjson.PARAM_ERROR)
    
    datas = q.filter(Order.paid_time >= start).filter(Order.paid_time < end).group_by('paid_date').all()

    # 数据处理
    format_result_datas = format_array_data_to_dict(datas, 'paid_date')
    return resjson.print_json(0, u'ok', {'data':format_result_datas, 'date_norms':date_norms})
