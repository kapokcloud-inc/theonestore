# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.helpers import log_error
from app.helpers import toamount

def format_amount(sourcePrice=0, format_type=0):
    ''' 处理商品价格显示 
        @param sourcePrice, 源价格
        @param format_type, 转换类型 
                0=为0则为整数0，小数均为0则返回整数，否则保留两位小数
                1=为0则为整数0.00，否则均保留两位小数
    '''
    if sourcePrice == None or sourcePrice == 0:
        if format_type == 1:
            return toamount(0)
        return 0

    try:
        if isinstance(sourcePrice, types.IntType) or isinstance(sourcePrice, types.FloatType):
            #限制保留2位小数
            sourcePrice = toamount(sourcePrice)
        else:
            raise ValueError('参数类型错误')
    except Exception:
        if isinstance(sourcePrice, (int,float)):
            #限制保留2位小数
            sourcePrice = toamount(sourcePrice)
        else:
            raise ValueError('参数类型错误')

    

    if format_type == 0:
        #小数均为0则返回整数，否则保留两位小数
        decmiclist = list((str(sourcePrice).split('.'))[1])
        if decmiclist and decmiclist[0] == '0' and decmiclist[1] == '0':
            return int(sourcePrice)
        else:
            return sourcePrice
            
    elif format_type == 1:
        return sourcePrice
  
    
def format_avatar(soruceImg, avatartype = 1):
    """ 处理头像路径 
    @param soruceImg, 源图片url
    @param avatartype, 头像类型
            0:-square.micro, 超小正方形50x50
            1:-square.small, 小正方形100x100
            2:-square.middle, 中正方形200x200
            3:-square.large, 大正方形400x400
            4:-square.giant, 超大正方形800x800
    """

    if not soruceImg:
        return ''

    http = 'http:'
    https =  'https:'
    # http://theonestore.cn/default.png => //theonestore.cn/default.png
    if soruceImg[:5] == http:
        soruceImg = soruceImg[5:]
    
    # https://theonestore.cn/default.png => //theonestore.cn/default.png
    elif soruceImg[:6] == https:
        soruceImg = soruceImg[6:]

    imgtypes = {
        0:'-square.micro', 
        1:'-square.small', 
        2:'-square.middle', 
        3:'-square.large', 
        4:'-square.giant', 
    }

    # 微信头像
    if soruceImg.find('qlogo.cn') != -1:
        return soruceImg

    # 阿里云或者七牛图片资源
    return soruceImg + imgtypes[avatartype]
