#!/usr/bin/env python3
#-*-coding:utf-8-*-
import os
import xlrd
#
#root目录
#rootdir = "F:\\work\\workspace\\workspace1.1\\file\\IT\\项目级\\TMS-周迭代\\"
rootdir = 'F:\\2018svn\\项目级\\TMS-周迭代'

#搜索关键字
key_word = "TRADE_ORDER_GATHER_KEY"

def walk_all_files(rootdir ,query):
    print(os.walk(rootdir))
    for parent,dirnames,filenames in os.walk(rootdir):
        # for dirname in dirnames:
        #     print("parent is :"+parent)
        #     print("dirname is:"+dirname)
        #     pass
        ##print(filenames)
        for filename in filenames:
            #print("fileName:"+filename)
            is_file_contain_word(os.path.join(parent,filename),query)

def is_file_contain_word(file_,query_word):
    #print("search file:" + file_)
    file_suffix = os.path.splitext(file_)[1]
    #过滤掉非excel的
    if file_suffix != '.xls' and file_suffix != '.xlsx':
        #print("file_suffix:"+file_suffix)
        return
    #过滤临时文件
    if '~$' in file_:
        return
    #print("file_suffix:" + file_)
    workbook = xlrd.open_workbook(file_)
    sheet_names = workbook.sheet_names()
    #all_value = workbook.sheet_by_index(0)
    for sheet_all_values in workbook.sheets():
        row_length = sheet_all_values.nrows
        for i in range(row_length):
            rows = sheet_all_values.row_values(i)
            col_length = sheet_all_values.ncols
            for j in range(col_length):
                #print(rows[j])
                if query_word in str(rows[j]).upper():
                    print(file_)
                    #print(rows[j].encode('utf8'))

walk_all_files(rootdir,key_word.upper())

print("done")