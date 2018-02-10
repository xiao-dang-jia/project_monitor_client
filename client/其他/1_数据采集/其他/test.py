#!/usr/bin/python
# -*- coding: UTF-8 -*-


import sys
import sched
import time

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')


schedule = sched.scheduler(time.time, time.sleep)

def func(string1,float1):
    print "Now is",time.time()," | output=",string1,float1

print time.time()

schedule.enter(2,0,func,("test1",time.time()))
schedule.run()