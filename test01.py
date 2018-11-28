# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: xing yan
"""

from mako.template import Template


mytemplate = Template("hello ${name}")

print(mytemplate.render(name="jack"))