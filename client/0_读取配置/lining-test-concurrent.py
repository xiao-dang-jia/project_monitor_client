#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 12/1/18
"""
function:

"""
import sys

#解决 二进制str 转 unicode问题
# reload(sys)
# sys.setdefaultencoding('utf8')

from collections import deque
import threading
import sys
import os
import string
import logging
import time
import datetime
from optparse import OptionParser
import ConfigParser
import random
import uuid
import psycopg2

# 解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

## 全局变量
conn = psycopg2.connect(database="dw", user="gpadmin", password="gpadmin", host="10.4.33.151", port="5432")
DATE_TODAY = datetime.datetime.strftime(datetime.date.today(), '%Y-%m-%d')
DATE_YESTERDAY = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1), '%Y-%m-%d')
ERR_LOG_PATH = "/tmp/kettle/run_sqlscript/"
ERR_AMTCHING_LIST = ["FAILED:", "ERROR:"]

# 脚本执行日志
SEP_HYPHEN = "--------------------"
SEP_ASTERISK = "********************"
SEP_PLUS = "++++++++++++++++++++"
SEP_TILDE = "~~~~~~~~~~~~~~~~~~~~"


# log相关
def setup_logger(logger_name, log_file, level=logging.INFO):
    """
    创建logger对象
    :param logger_name:
    :param log_file:
    :param level:
    :return:
    """
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)



class Run_script:
    """自定义run_script类，需要完整文件名和分析时间进行初始化"""

    def __init__(self, filename, analysisdate):
        self.filename = filename
        self.analysisdate = analysisdate

    def insert_begin(self, filename, start_time_formatted, task_uuid, thread_id):
        """往数据库中插入日志"""
        pass

    def update_end(self, end_time_formatted, task_spend, task_uuid, task_status, log_message, orignal_command):
        """往数据库中插入日志"""
        pass

    def start(self):
        """运行sql脚本"""
        print("SQL脚本调用开始运行:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        for i in range(5):
            time.sleep(random.choice(range(3)))
            print("SQL脚本正在执行:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print("SQL脚本调用执行完成:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

def run_concurrently(task_list):
    task_queue = deque()
    analysisdate = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1), '%Y-%m-%d')

    # 生成任务队列
    filename = task_list
    filename_arr = filename.split(",")
    script_objs = []
    for i in range(len(filename_arr)):
        script_objs.append(Run_script(filename_arr[i], analysisdate)) # 执行脚本列表生成完成

    # generate the task queue
    for task in script_objs:
        task_queue.append(task)

if __name__ == '__main__':
    try:
        task_list = "./lining-dw/2_开发/1_data_source/7_file_data/22_情报通.sql,./lining-dw/2_开发/1_data_source/7_file_data/27_京东自营.sql,./lining-dw/2_开发/1_data_source/7_file_data/06_京东店铺数据.sql,./lining-dw/2_开发/1_data_source/7_file_data/30_商品信息爬虫.sql,./lining-dw/2_开发/1_data_source/7_file_data/05_淘宝店铺数据.sql,./lining-dw/2_开发/1_data_source/7_file_data/07_商品活动日期_输入.sql,./lining-dw/2_开发/1_data_source/7_file_data/99_商品清单.sql,./lining-dw/2_开发/1_data_source/7_file_data/08_维品会结算数据.sql,./lining-dw/2_开发/1_data_source/7_file_data/20_名鞋库_爬虫整理数据.sql,./lining-dw/2_开发/1_data_source/1_erp_data/1_增量更新表_新增.sql,./lining-dw/2_开发/1_data_source/7_file_data/21_经销_增量更新表.sql,./lining-dw/2_开发/1_data_source/4_plat_data/25_淘宝平台SPU维表.sql,./lining-dw/2_开发/1_data_source/4_plat_data/26_官网订单表.sql,./lining-dw/2_开发/1_data_source/7_file_data/25_spu.sql,./lining-dw/2_开发/1_data_source/1_erp_data/25_spu.sql,./lining-dw/2_开发/1_data_source/7_file_data/28_运营费用.sql,./lining-dw/2_开发/1_data_source/7_file_data/04_官网店铺数据_omniture.sql"
        run_concurrently(task_list)

    except Exception as e:
        print(e)