#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 13/1/18
"""
function:
监控程序入口
"""
import sys
import datetime
# 自定义模块
import monitor_class
import configure
import scheduler
import initialisation

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

## 需要手动配置
host_ip = 'rm-bp1tby5h17t84ddpf.mysql.rds.aliyuncs.com'
db_nick = '爱哆哆配置数据库'
username = 'syadmin'
password = 'tXo8fe2dYfkf'
port = '3306'
database = 'bigdata_monitor'
API_URL = 'http://bi.bigdata.fenxibao.com/monitor_web/api/collect'

if __name__ == '__main__':
    try:
        print('1. main.py: 开始读取数据库配置')
        config_db_obj = monitor_class.DB(host_ip, db_nick, username, password, port, database)

        # 生成配置列表
        server_service_obj_list = configure.gen_server_service_obj_list(config_db_obj)
        for server_service_obj in server_service_obj_list:
            scheduler.Task(server_service_obj).genSchedule()
        print('2. main.py: 所有任务配置完成!')

        # 初始化next_checktime
        current_time = datetime.datetime.now()
        for server_service_obj in server_service_obj_list:
            initialisation.initialise_next_checktime(current_time, config_db_obj, server_service_obj)
        print('3. main.py: 初始化next_checktime完成\n等待任务启动中...')

        # 启动所有的任务
        scheduler.sched.start()
        print('4. main.py: 所有任务启动完成!')
    except Exception, e:
        print e
