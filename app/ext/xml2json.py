#coding:utf-8
u'''
xml转json
不考虑xml标签属性
'''
from xml.etree import ElementTree

def xml2json(s):
    root = ElementTree.fromstring(s)
    #初始化
    result = {root.tag:_parse(root)}
    return result

def _parse(ele):
    result = None
    tags = []
    p_childs = []
    for child in ele.getchildren():
        #统计子元素
        tags.append(child.tag)
        #递归调用自身
        p_childs.append((child.tag, _parse(child)))
    
    if not tags:
        #文本处理
        text = ele.text
        if text is not None:
            text = text.strip()
        else:
            text = ''
        return text
    
    if len(set(tags)) < len(tags):
        #列表处理 子元素存在不同标签则为列表
        result = []
        result = [dict([x]) for x in p_childs]
    else:
        #字典处理
        result = {}
        result = dict(p_childs)
    return result



if __name__ == "__main__":
    s = '''<?xml version="1.0" encoding="utf-8"?>
    <root>
    <eventAttributes>
    <eventType>Not Known</eventType>
    <logisticsPath>1/64010/5227</logisticsPath>
    <parkingEventIds>
      <parkingEventId>9426793</parkingEventId>
    </parkingEventIds>
      </eventAttributes></root>'''
    with open('aaa.xml', 'r') as f:
        s = f.read()
    obj = xml2json(s)
    print (obj)
    #from xmlutils.xml2json import xml2json
    #obj = xml2json('aaa.xml').get_json()
    #import json
    #obj = json.loads(obj)
