# -*- coding: utf-8 -*-
"""
Created on 2018/8/9

@author: xing yan
"""

import os

rs = os.popen("svn update ./svn/tms/ F:\\2018svn\\项目级\\TMS-周迭代 --password yang.zhou --non-interactive")

r2 = os.popen("svn info F:\\2018svn\\项目级\\TMS-周迭代")

# print(rs.readlines())

print(r2)
for line in r2:
    # print(line)
    print(line.split("\n")[0])