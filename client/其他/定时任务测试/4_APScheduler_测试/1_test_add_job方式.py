#!/usr/bin/python
# -*- coding: UTF-8 -*-


import sys
import time
import os
import sched
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler


#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

sched = BlockingScheduler()
class Task():
    def __init__(self):
        pass
    def timed_job(self):
        """调度器1：按频率执行"""
        print('This job is run every second.')


    # @sched.scheduled_job('cron', day_of_week='mon-fri', hour='0-23', minute='0-59', second='*/4')
    # def scheduled_job(self):
    #     """调度器2：每天定点执行"""
    #     print('This job is run every weekday at 5pm.')

sched.add_job(Task.timed_job,'interval',seconds=1)
print('before the start function')
sched.start()
print("let us figure out the situation")