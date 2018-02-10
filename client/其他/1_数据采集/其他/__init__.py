#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/1/18
"""
function:

"""
import sys

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    try:
        pass
    except Exception, e:
        print e