#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:

"""
import sys

#解决 二进制str 转 unicode问题
# reload(sys)
# sys.setdefaultencoding('utf8')





if __name__ == '__main__':
    try:
        command = """cat /etc/issue|grep "CentOS\""""
        result = """CentOS release 6.9 (Final)"""
        if "CentOS" in result:
            print "HAHA"
        # print command
    except Exception as e:
        print(e)