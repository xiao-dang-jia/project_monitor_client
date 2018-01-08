#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/1/18
"""
function:
从数据库中读取配置
"""
import threading
import time
import sys
import os
import string
import time
import datetime
from optparse import OptionParser
import ConfigParser
import json
import abc
from abc import ABCMeta, abstractmethod
import traceback
import psycopg2
from apscheduler.schedulers.background import BlockingScheduler
import logging
import paramiko


import monitor_1_configure
import monitor_2_class
import monitor_4_post

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()
sched=BlockingScheduler()

# 配置数据库
configure_hostip = 'localhost'
configure_username = 'youshaox'
configure_password = '12345'
configure_database = 'monitor_configuration'

################
# 公共函数区
################

def toDict(**kwargs):
    """
    格式化为字典
    :param kwargs:
    :return:
    """
    for key in kwargs.keys():
        globals()[key] = kwargs[key]
    return kwargs

def getTransformedTime(in_time_str):
    """
    将period类型时间转换为统一的单位（秒）
    :param in_time_str:
    :return: 返回时间（int）
    """
    # 截取数字
    time_str_arr = in_time_str.split(" ")
    time_value = time_str_arr[0]
    time_unit = time_str_arr[1]

    if time_unit == 's':
        return int(time_value)
    if time_unit == 'min':
        return int(time_value)*60
    if time_unit == 'hour':
        return int(time_value)*3600
    else:
        return 0
        # raise ValueError("暂时不支持当前时间格式。请按当前时间格式输入：数字 s/min/hour")


def getFormattedTime(in_time_str):
    """
    格式化时间
    :param in_time_str: 配置时间
    :return: 格式化的配置时间（字典）
    :raise TypeError: 如果输入的字符串格式不符合
    """
    try:
        time_str_arr = in_time_str.split(' ')

        date_str = time_str_arr[0]
        time_str = time_str_arr[1]

        # 处理日期
        out_year = date_str.split('-')[0]
        out_month = date_str.split('-')[1]
        out_day = date_str.split('-')[2]

        out_hour = time_str.split(':')[0]
        out_minute = time_str.split(':')[1]
        return toDict(year=out_year, month=out_month, day=out_day, hour=out_hour, minute=out_minute)
    except Exception as e:
        raise TypeError('定点执行时间配置错误!%s' %e)

def runTaskByTimeType(target,in_time_dict):
    """
    添加计划任务

    :param target: 目标执行函数
    :param in_time_dict: 配置时间详细
    :return:
    """
    if in_time_dict['time_type'] == 'period':
        # 需要做个时间转换
        time_value = getTransformedTime(in_time_dict['time_value'])
        sched.add_job(target, 'interval',seconds=time_value)

    elif in_time_dict['time_type'] == 'time':
        # 获取格式化时间
        time_value = getFormattedTime(in_time_dict['time_value'])
        sched.add_job(target, 'cron',
                      year=time_value['year'], month=time_value['month'], day=time_value['day'],
                      hour=time_value['hour'], minute=time_value['minute'])

# 获取系统版本
def verifySystemVersion(host_obj):
    """
    获取服务器上的系统版本，并处理为相应的字段
    :param host_obj:
    :return: 系统版本(String)
    """
    ssh = monitor_2_class.ssh_server(host_obj)
    command = """cat /etc/issue|grep "%s\""""%host_obj.version
    ssh_stdin, ssh_stdout_basic, ssh_stderr = ssh.exec_command(command)

    # 判断系统版本
    if ssh_stdout_basic is not None and ssh_stderr is None:
        return True
    else:
        return False


class Task():
    def __init__(self,server_service_obj):
        self.server_service_obj = server_service_obj

    def run(self):
        print("1. Task 开始了")
        host_obj = self.server_service_obj.host_obj
        service_dict = self.server_service_obj.service_dict

        # 实例化数据库对象
        db_detail = service_dict['db_detail']
        db_object = monitor_2_class.DB(db_detail['host_ip'],db_detail['db_nick'],db_detail['username'],db_detail['password'],db_detail['port'],db_detail['database'])

        m_type = service_dict['m_type']
        m_dim_dict = service_dict['m_dim']
        # 根据传入的服务来生成任务
        for key in m_dim_dict:
            if key != 'version':
                genSchedule(host_obj,db_object,m_type,key,m_dim_dict[key])

def genSchedule(host_obj,db_object,m_type,service,in_time_dict):
    """
    根绝服务类型，监控项和监控配置：生成配置
    :param m_type:
    :param service:
    :param in_time_dict: 详细时间配置
    :return:
    """
    # server
    if m_type == 'server' and verifySystemVersion(host_obj):
        # centos
        if host_obj.version == 'centos':
            centos_monitor_server_obj = monitor_2_class.Centos_monitor_server(host_obj)

            # 1. cpu 监控
            if service == 'cpu-usage':
                runTaskByTimeType(centos_monitor_server_obj.runCPU(), in_time_dict)
            # 2. disk 监控
            elif service == 'disk-usage':
                runTaskByTimeType(centos_monitor_server_obj.runDisk(), in_time_dict)
            # 3. IOPS 监控
            elif service == 'IOPS-usage':
                runTaskByTimeType(centos_monitor_server_obj.runIOPS(), in_time_dict)
            # 4. memory 监控
            elif service == 'memory-usage':
                runTaskByTimeType(centos_monitor_server_obj.runMemory(), in_time_dict)
    # kettle
    elif m_type == 'kettle':
        # 如果是kettle
        kettle_monitor_obj = monitor_2_class.Kettle_monitor(host_obj)

        if service == 'process':
            runTaskByTimeType(kettle_monitor_obj.check_process(),in_time_dict)
    # gp
    elif m_type == 'gp':
        gp_monitor_obj = monitor_2_class.GP_monitor(host_obj,db_object)
        if service == 'check-connections':
            runTaskByTimeType(gp_monitor_obj.check_connections(), in_time_dict)
        elif service == 'master-status':
            runTaskByTimeType(gp_monitor_obj.check_master(), in_time_dict)
        elif service == 'segment-status':
            runTaskByTimeType(gp_monitor_obj.check_segment(), in_time_dict)
    # newbi
    elif m_type == 'newbi':
        newBI_monitor_obj = monitor_2_class.NewBI_monitor(host_obj)
        if service == 'process':
            runTaskByTimeType(newBI_monitor_obj.check_process(), in_time_dict)
        elif service == 'login':
            runTaskByTimeType(newBI_monitor_obj.check_login(), in_time_dict)

    else:
        raise ValueError('未知的服务！')



if __name__ == '__main__':
    try:
        # test
        # host_obj = monitor_2_class.Host('172.18.21.196','lining-kettle','root','shuyun196','centos')
        # service_dict = {"m_type":"kettle","db_detail":" ","m_dim":{"version":"pdi","process":{"time_type":"period","time_value":"10s"}}}

        host_obj = monitor_2_class.Host('172.18.21.179','lining-gp','root','shuyun179','centos')
        service_dict = {"m_type":"gp","db_detail":\
            {"host_ip":"172.18.21.179","db_nick":"lining_data_center","username":"gpadmin","password":"gpadmin","port":"5432","database":"data_center"}\
                ,"m_dim":{"version":"4.3.11","check-connections":{"time_type":"period","time_value":"10s"}}}
        print service_dict['db_detail']
        #
        print("+++")
        server_service_obj = monitor_2_class.Server_service(host_obj,service_dict)
        print("---")
        Task(server_service_obj).run()
        sched.start()
    except Exception, e:
        print e

