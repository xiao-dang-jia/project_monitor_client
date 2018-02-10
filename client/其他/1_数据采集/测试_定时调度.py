#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""API更改前的代码"""

import sys
import time

import urllib,urllib2
from apscheduler.schedulers.background import BlockingScheduler
import logging
logging.basicConfig()
#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

sched = BlockingScheduler()

def urlPost(postdata):
    data = urllib.urlencode(postdata)
    req = urllib2.Request('http://172.18.21.245:8080/moniter/api/collect', data)
    response = urllib2.urlopen(req)
    return response.read()

def format_json(project_nick,host_nick,db_nick,m_type,m_dim,m_value,m_logger,m_timestamp):
    """返回一个JSON类型数据"""
    data = {"project_nick":project_nick,\
            "host_nick":host_nick,\
            "db_nick":db_nick,\
            "m_type":m_type,\
            "m_dim":m_dim,\
            "m_value":m_value,\
            "m_logger":m_logger,\
            "m_timestamp":m_timestamp}
    return data

# second = 3

class Check():
    def __init__(self):
        pass
    @sched.scheduled_job('interval', seconds=10,args=('self',))
    def run_check(self):
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        urlPost(format_json('test-sched','lining-host1','server',None,'use-cpu','30%','TEST-LOG',m_timestamp))
        print('I am running at '+m_timestamp)

class Task():
    """"""
    def __init__(self):
        pass

    def run(self):
        check_obj = Check()
        # sched.add_job(check_obj.run_check, 'interval', seconds=1)
        print('before the start function')
        sched.start()
        print("let us figure out the situation")
if __name__== '__main__':
    Task().run()

