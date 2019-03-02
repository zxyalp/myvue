# -*- coding: utf-8 -*-
"""
Created on 2018/11/18

@author: xing yan
"""
import sys

sum = 0

for line in sys.stdin: sum += int(line)

print(sum)