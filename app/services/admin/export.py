# -*- coding: utf-8 -*-
"""
    theonestore
    https://github.com/kapokcloud-inc/theonestore
    ~~~~~~~~~~~
    
    :copyright: © 2018 by the Kapokcloud Inc.
    :license: BSD, see LICENSE for more details.
"""
from flask_babel import gettext as _
import flask_excel as excel


class ExportService(object):
    """导出service"""
    def __init__(self, data_list, field_list, file_name='', file_type='xlsx'):
        """初始化函数
        :param data_list 数据列表
        :param field_list 字段列表
        :param filename 导出文件名称
        :param file_type 文件类型 csv|xls|xlsx|xml|json
        """
        self.data_list = data_list
        self.field_list = field_list
        self.file_name = file_name
        self.file_type = file_type

    
    def export(self):
        """导出"""
        return self._excel()


    def _excel(self):
        """excel数据"""
        sheet = []
        sheet_title_list = [field['title'] for field in self.field_list]
        sheet.append(sheet_title_list)

        for data in self.data_list:
            row_data = []
            for field in self.field_list:
                field_name = field.get('field', None)
                func = field.get('func', None)
                val = ''
                if field_name and func is None:
                    val = getattr(data, field_name, '')
                elif field_name and func:
                    val = getattr(data, field_name, '')
                    val = func(val)
                elif not field_name and func:
                    val = func(data)
                    
                row_data.append(val)
            sheet.append(row_data)
        
        return excel.make_response_from_array(sheet, self.file_type,
                                sheet_name = 'Sheet1',
                                file_name = self.file_name)



