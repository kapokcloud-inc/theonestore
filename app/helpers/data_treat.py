# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""

from app.helpers import log_info
from app.helpers import toamount

def format_amount(sourcePrice=0):
    ''' 处理商品价格显示 '''
    try:
        if isinstance(sourcePrice,types.IntType) or isinstance(sourcePrice,types.FloatType):
            #限制保留2位小数
            sourcePrice = toamount(sourcePrice)
    except Exception:
        if isinstance(sourcePrice,(int,float)):
            #限制保留2位小数
            sourcePrice = toamount(sourcePrice)

    try:
        targetPrice = 0
        if sourcePrice == None or sourcePrice == 0:
            return targetPrice

        decmiclist = (sourcePrice.split('.'))[1]
        #小数均为0则返回整数，否则保留两位小数
        if decmiclist and decmiclist[0] == 0 and decmiclist[1] == 0:
            targetPrice = int(sourcePrice)
            return targetPrice
        else:
            targetPrice = sourcePrice
            return targetPrice
    except ValueError as e:
        print(e)
    
def format_avatar(soruceImg,avatartype = 0):
    ''' 处理头像路径 '''
    if soruceImg == None or soruceImg == "":
        return ''

    if soruceImg.find('thirdwx.qlogo.cn') == -1 and soruceImg.find('aliyun.kapokcloud.com') == -1:
        return soruceImg

    soruceImg = soruceImg.replace('http:','')
    soruceImg = soruceImg.replace('https:','')

    imgtypes = {0:'-square.small', 1:'-square.middle', 2:'-square.micro', 3:'-square.large', 4:'square.large', 5:'square.giant'}

    #微信头像或已是七牛小图则返回原图，否则在是七牛资源的前提下拿小图(头像样式)
    if soruceImg.find('thirdwx.qlogo.cn') != -1 or soruceImg.find(imgtypes[avatartype]) != -1:
        return soruceImg
    else:
        return soruceImg + imgtypes[avatartype]
    