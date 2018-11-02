# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: xing yan
"""

d = {'s':11, 'a':122}

s = "shsuhsuns{s}{a}"

s1=s.format(**d)

print(s1)