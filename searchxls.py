# -*- coding: utf-8 -*-
"""
Created on 2018/10/26

@author: xing yan
"""
import os
import xlrd
from openpyxl import Workbook, load_workbook

basedir = 'F:\\2018svn\\项目级\\TMS-周迭代'

file_type = ('.xls', '.xlsx')

s = 'funddealorderdtl'


def get_excel_files(base_dir):
    excel_files = []

    for root, dirs, files in os.walk(base_dir):
        abs_path_files = [os.path.join(root, f) for f in files]
        excel_files.extend(list(filter(filter_file_type, abs_path_files)))
    return excel_files


def filter_file_type(f):
    """
    判断文件类型为.xls/.xlsx and 文件名称包含CCMS关键字
    :param f:
    :return:
    """
    return os.path.splitext(f)[1] in ('.xls', '.xlsx') and 'CCMS' in os.path.basename(f).upper()


def search_word(word, base_dir):
    """
    在给定的路径所有excel文件中搜索word字符串,如果搜索到结果，返回文件路径列表
    :param word:
    :param base_dir:
    :return:
    """

    result_file = []

    files = get_excel_files(base_dir)
    for file in files:
        excel_file = search_excel_word(word, file)
        result_file.extend(excel_file)

    return result_file


def search_excel_word(word, file):
    excel_file = []
    book = xlrd.open_workbook(file)
    for t in range(book.nsheets):
        sheet = book.sheet_by_index(t)
        for row in range(1, sheet.nrows):
            row_values = sheet.row_values(row)
            for cell in row_values:
                if word.upper() in cell.upper():
                    excel_file.append((file, row_values))
    return excel_file


e = 'F:\\2018svn\\项目级\\TMS-周迭代\\3.0.2\\4-上线发布\\配置\\CCMS配置-ADD-产线环境.xls'

res = search_word('queue_total_redeem_job', basedir)

for r, desc in res:
    print(r, desc)

#
# if __name__ == '__main__':
#     excel = get_excel_files(basedir)
#     print(excel)

