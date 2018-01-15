#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 13/1/18
"""
function:
监控程序入口
"""
import sys

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

import monitor_1_configure
import monitor_3_develop

if __name__ == '__main__':
    try:
        ## 需要手动配置
        host_ip = '172.18.21.245'
        db_nick = '李宁配置数据库'
        username = 'root'
        password = '54321'
        port = '5432'
        database = 'mydata'

        # 生成配置列表
        server_service_obj_list = monitor_1_configure.gen_server_service_obj_list(host_ip, db_nick, username,
                                                                                  password, port, database)
        for server_service_obj in server_service_obj_list:
            monitor_3_develop.Task(server_service_obj).genSchedule()
        print('所有任务配置完成!')
        # 启动所有的任务
        monitor_3_develop.sched.start()
        print('所有任务启动完成!')
    except Exception, e:
        print e