# -*- coding: utf-8 -*-
"""
Created on 2018/8/9

@author: xing yan
"""
import json

with open("D:\\take\\sub.json", encoding='utf-8') as r:
    sub = json.load(r)
    print(sub)

for k, v in sub.items():
    k1=k[0].upper()+k[1:]
    print('request.set%s(context.getParameter("%s"));'%(k1, k))
