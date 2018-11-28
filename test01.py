# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: xing yan
"""

a={'a':1,'b':2,'c':3}

def fn(**kw):
    print(kw)

    for k,v in kw.items():
        print('{}={}'.format(k,v))

print()
print()
