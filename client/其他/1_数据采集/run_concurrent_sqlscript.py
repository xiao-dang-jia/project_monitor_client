#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time
import sys
import os
import string
import time
import datetime
from optparse import OptionParser
import ConfigParser
import random
import uuid
import psycopg2

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

## 全局变量
conn = psycopg2.connect(database="dw", user="gpadmin", password="gpadmin", host="10.4.33.151", port="5432")
DATE_TODAY = datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d')
DATE_YESTERDAY = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=1),'%Y-%m-%d')
ERR_LOG_PATH = "/tmp/kettle/run_sqlscript/"
ERR_AMTCHING_LIST = ["FAILED:","ERROR:"]

# 创建类
# 每一个操作自己的对象
# 注意锁的位置，否则变成单线程了

class Run_script:
    """自定义run_script类，需要完整文件名和分析时间进行初始化"""
    def __init__(self,filename,analysisdate):
        self.filename = filename
        self.analysisdate = analysisdate

    def insert(self, filename, start_time_formatted, end_time_formatted, time_spend, task_uuid, thread_id, task_status, log_message, orignal_command):
        """往数据库中插入日志"""
        filename_arr = filename.split("/")
        if (len(filename_arr)) == 6:
            task_name = filename_arr[len(filename_arr) - 1]
            task_location = filename
            task_group = filename_arr[len(filename_arr) - 3]
        elif (len(filename_arr) == 5):
            task_name = filename_arr[len(filename_arr) - 1]
            task_location = filename
            task_group = filename_arr[len(filename_arr) - 2]
        else:
            task_name = filename_arr[len(filename_arr) - 1]
            task_location = filename
            task_group = "unknown"
        cur = conn.cursor()
        query1 = cur.mogrify('insert into dw.monitor_concurrent_tasks_log values(%s,%s,%s);',(str(task_uuid), log_message, orignal_command))
        cur.execute(query1)
        query2 = cur.mogrify('insert into dw.monitor_concurrent_tasks values(%s,%s,%s,%s,%s,%s,%s,%s,%s);',(str(task_group),str(task_location),str(task_name),str(task_uuid),str(thread_id),task_status,start_time_formatted,end_time_formatted,time_spend))
        cur.execute(query2)
        conn.commit()

    ## 启动
    def start(self):
        """运行sql脚本"""
        print("程序开始运行:%s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        start_time = time.time()
        start_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        task_uuid = uuid.uuid1()

        # 加载
        filename = self.filename
        f = open(filename)
        sqlScript = f.read()
        f.close()

        # 提取文件名,为错误输出文件名
        result = os.system("mkdir -p " + ERR_LOG_PATH)
        filename_arr = filename.split("/")
        errLogName = ERR_LOG_PATH + filename_arr[len(filename_arr) - 3] + "_" + filename_arr[
            len(filename_arr) - 2] + "_" + filename_arr[len(filename_arr) - 1] + ".log"
        command = sqlScript.replace('${analysis_date}', str(analysisdate))
        command = "psql -h 10.4.33.151 -U gpadmin --no-password -d dw -c \"" + command + " \nselect '执行文件：" + filename + "' as filename,now();\" 2>" + errLogName

        # 检测异常
        log_message = ""
        result = os.system(command)
        print("result:" + str(result))

        errfile = open(errLogName)
        errlog = errfile.read()
        errfile.close()
        log_message = errlog
        task_status = "sucess"
        if result != 0:
            ## 如果报错，那么状态为失败
            task_status = "fail"
        end_time = time.time()
        time_spend = end_time - start_time
        end_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        thread_id = threading.current_thread().name
        # 要不要插入，并不是SQL文件本身报错了，只是脚本跑报错了
        self.insert(filename, start_time_formatted, end_time_formatted, time_spend, task_uuid, thread_id,
                    task_status, log_message, command)
        print("程序结束运行:%s,耗时(秒):%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), end_time - start_time))


class StoppableThread(threading.Thread):  # 继承父类threading.Thread
    """线程类，参数为threadID和脚本对象script进行初始化"""
    def __init__(self,threadID,script):
        super(StoppableThread,self).__init__()
        # threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.threadID = threadID
        self.script = script

    def stop(self):
        """The thread itself has to check regularly for the stopped() condition."""
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("Starting Thread" + str(self.threadID))
        print("------------------------------------------------------------当前线程总数为:" + str(
            len(threading.enumerate())) + "------------------------------------------------------------")
        self.script.start()
        print("Exiting Thread" + str(self.threadID))
        threadmax.release()

def get_tasks_by_configure_file(configure_file):
    """输入一个配置文件，返回该配置文件的一个任务列表"""
    cf = ConfigParser.ConfigParser()
    cf.read(configure_file)
    task_list = []
    for section in cf.sections():
        file_str = ""
        #  连接这个SECTION里的所有文件
        ## 这是一个PART_1的列表，列表中为多个TUPLE,连接这里面TUPLE的第二个
        for counter, item in enumerate(cf.items(section)):
            ## 判断是否为最后一个
            ## 如果是最后一个，不加逗号
            if counter == len(cf.items(section)) - 1:
                file_str = file_str + item[1]
            else:
                file_str = file_str + item[1] + ","
        task_list.append(file_str)
    return task_list

def run_concurrently(task_list):
    """输入一个TASK队列，执行这个TASK队列"""
    filename = task_list
    filename_arr = filename.split(",")
    # 对象列表
    # 创建脚本对象列表 script_objs
    script_objs = []
    for i in range(len(filename_arr)):
        script_objs.append(Run_script(filename_arr[i], analysisdate))

    # 线程列表
    threads = []
    for i in range(len(script_objs)):
        threads.append(StoppableThread(i, script_objs[i]))

    for thread in threads:
        threadmax.acquire()
        thread.setDaemon(False)
        thread.start()
    # 阻塞主线程
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    # 命令行参数解析;注意参数不可带空格
    usage = "usage: %prog [options] -f filename "
    parser = OptionParser(usage=usage, version="%prog 1.0")

    parser.add_option("-f", "--filename", action="store_true",
                      dest="filename",
                      default=False,
                      help="Script file name")

    parser.add_option("-d", "--analysisdate", action="store_true",
                      dest="analysisdate",
                      default=False,
                      help="Business execution date")
    (options, args) = parser.parse_args()

    if options.filename is not True:
        parser.error("filename is not empty !")
    else:
        filename = args[0]
        print 'params filename:' + filename + ' check success !'

    if options.analysisdate is not True:
        analysisdate = DATE_YESTERDAY
    else:
        analysisdate = args[1]
        print 'params analysisdate:' + analysisdate + ' check success !'

    try:
        # file name
        threadmax = threading.BoundedSemaphore(3)
        task_queue_list = get_tasks_by_configure_file(filename)
        print("------------------------------------------------------------This is "+filename+"------------------------------------------------------------")
        ## 对每一个任务队列
        for task_queue in task_queue_list:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx这是"+ task_queue +"的开始xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            run_concurrently(task_queue)
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx这是"+ task_queue +"的结束xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        ## 并发执行这个TASK,列表

        # StoppableThread.join()
        print("------------------------------------------------------------exiting main thread------------------------------------------------------------")
    except Exception as e:
        raise ValueError(e)

#
# drop table if exists dw.monitor_concurrent_tasks;
# create table dw.monitor_concurrent_tasks(
# 	task_group varchar(255)
# 	,task_location varchar(255)
# 	,task_name varchar(255)
# 	,task_uuid varchar(255) -- 按跑的时间分出的唯一id
# 	,task_thread_id varchar(255)
# 	,task_status varchar(255) -- 任务是否成功 sucess or fail
# 	,task_start timestamp
# 	,task_end timestamp
# 	,task_spend numeric(19,4)
# 	,timestamp_v timestamp default now()
# ) distributed by (task_group)
# ;
#
#
# #
# drop table if exists dw.monitor_concurrent_tasks_log;
# create table dw.monitor_concurrent_tasks_log(
# 	uuid varchar(255)
# 	,log_message varchar
# 	,command varchar
# 	,timestamp_v timestamp default now()
# ) distributed by (command)
# ;
