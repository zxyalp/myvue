# -*- coding: utf-8 -*-
"""
Created on 2018/8/9

@author: xing yan
"""

import os

rs = os.popen("svn update ./svn/tms/ F:\\2018svn\\项目级\\TMS-周迭代 --password yang.zhou --non-interactive")

# print(rs.readlines())

for line in rs:
    # print(line)
    print(line.split("\n")[0])