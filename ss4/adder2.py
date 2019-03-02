# -*- coding: utf-8 -*-
"""
Created on 2018/11/18

@author: xing yan
"""
import sys


sum = 0

while True:
    line = sys.stdin.readline()

    if not line: break

    sum += int(line)
print(sum)

