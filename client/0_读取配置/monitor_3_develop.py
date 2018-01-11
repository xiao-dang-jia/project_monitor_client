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


# import monitor_1_configure
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

# def getTransformedTime(in_time_str):
#     """
#     将period类型时间转换为统一的单位（秒）
#     :param in_time_str:
#     :return: 返回时间（int）
#     """
#     # 截取数字
#     time_str_arr = in_time_str.split(" ")
#     time_value = time_str_arr[0]
#     time_unit = time_str_arr[1]
#
#     if time_unit == 's':
#         return int(time_value)
#     if time_unit == 'min':
#         return int(time_value)*60
#     if time_unit == 'hour':
#         return int(time_value)*3600
#     else:
#         return 0
#         # raise ValueError("暂时不支持当前时间格式。请按当前时间格式输入：数字 s/min/hour")


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
    print "我开始运行"
    # 没有识别为一个函数
    print type(target)
    print "我结束运行"
    if in_time_dict['m_interval_type'] == 'period':
        # 需要做个时间转换
        time_value = int(in_time_dict['m_interval_time'])
        sched.add_job(target, 'interval',seconds=time_value)
    elif in_time_dict['m_interval_type'] == 'time':
        # 获取格式化时间
        time_value = getFormattedTime(in_time_dict['m_interval_time'])
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
    command = """cat /etc/issue|grep -i "%s\""""%host_obj.version
    ssh_stdin, ssh_stdout_basic, ssh_stderr = ssh.exec_command(command)
    # 判断系统版本
    if ssh_stdout_basic.read() is not None and len(ssh_stderr.read()) == 0:
        return True
    else:
        return False


class Task:
    def __init__(self,server_service_obj):
        self.server_service_obj = server_service_obj

    def genSchedule(self):
        """
        根据host_obj和db_obj和service_dict生成配置
        """
        print('生成一个任务')
        host_obj = self.server_service_obj.host_obj
        db_obj = self.server_service_obj.db_obj
        service_dict = self.server_service_obj.service_dict

        # server
        if service_dict["m_type"] == 'system' and verifySystemVersion(host_obj):
            # centos
            if host_obj.version == 'centos':
                centos_monitor_server_obj = monitor_2_class.Centos_monitor_server(host_obj)
                # 1. cpu 监控
                if service_dict["m_dim"] == 'cpu-usage':
                    # -todo 问题出在了加到任务中的过程，函数本身没有问题
                    runTaskByTimeType(centos_monitor_server_obj.check_CPU(), service_dict)
                # 2. disk 监控
                elif service_dict["m_dim"] == 'disk-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_disk(), service_dict)
                # 3. IOPS 监控
                elif service_dict["m_dim"] == 'IOPS-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_IOPS(), service_dict)
                # 4. memory 监控
                elif service_dict["m_dim"] == 'memory-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_memory(), service_dict)
        # kettle
        elif service_dict["m_type"] == 'kettle':
            # 如果是kettle
            kettle_monitor_obj = monitor_2_class.Kettle_monitor(host_obj)

            if service_dict["m_dim"] == 'process':
                runTaskByTimeType(kettle_monitor_obj.check_process(),service_dict)
        # gp
        elif service_dict["m_type"] == 'gp':
            gp_monitor_obj = monitor_2_class.GP_monitor(host_obj,db_obj)
            if service_dict["m_dim"] == 'check-connections':
                runTaskByTimeType(gp_monitor_obj.check_connections(), service_dict)
            elif service_dict["m_dim"] == 'master-status':
                runTaskByTimeType(gp_monitor_obj.check_master(), service_dict)
            elif service_dict["m_dim"] == 'segment-status':
                runTaskByTimeType(gp_monitor_obj.check_segment(), service_dict)
        # newbi
        elif service_dict["m_type"] == 'newbi':
            newBI_monitor_obj = monitor_2_class.NewBI_monitor(host_obj)
            if service_dict["m_dim"] == 'process':
                runTaskByTimeType(newBI_monitor_obj.check_process(), service_dict)
            elif service_dict["m_dim"] == 'login':
                runTaskByTimeType(newBI_monitor_obj.check_login(), service_dict)

        else:
            raise ValueError('未知的服务！')



if __name__ == '__main__':
    try:
        # test
        # host_obj = monitor_2_class.Host('172.18.21.196','lining-kettle','root','shuyun196','centos')
        # service_dict = {"m_type":"kettle","db_detail":" ","m_dim":{"version":"pdi","process":{"time_type":"period","time_value":"10s"}}}

        host_obj = monitor_2_class.Host('172.18.21.179','lining-gp','root','shuyun179','centos')
        db_obj = monitor_2_class.DB('172.18.21.179','data_center','gpadmin','gpadmin','5432','data_center')

        # service_dict = {"m_type":"gp","db_detail":\
        #     {"host_ip":"172.18.21.179","db_nick":"lining_data_center","username":"gpadmin","password":"gpadmin","port":"5432","database":"data_center"}\
        #         ,"m_dim":{"version":"4.3.11","check-connections":{"time_type":"period","time_value":"10s"}}}
        service_dict = {"m_type":"system","m_dim":"cpu-usage","m_interval_type":"period","m_interval_time":"10"}
        #
        server_service_obj = monitor_2_class.Server_service(host_obj,db_obj,service_dict)
        Task(server_service_obj).genSchedule()
        sched.start()
    except Exception, e:
        print e

