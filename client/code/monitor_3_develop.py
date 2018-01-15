#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/1/18
"""
function:
生成调度任务。
通过mointor_1_configure.py获得配置信息，以monitor_2_class中的监控任务为模版，生成调度任务。
"""

import sys
from apscheduler.schedulers.background import BlockingScheduler
import apscheduler
import logging
import monitor_2_class

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()
sched = apscheduler.BlockingScheduler\
    ()

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

# todo 商讨规定时间格式
def getFormattedTime(in_time_str):
    """
    格式化时间
    :param in_time_str: 配置时间
    :return: 格式化的配置时间（字典）
    :raise TypeError: 如果输入的字符串格式不符合
    2018-
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

def runTaskByTimeType(target, in_time_dict):
    """
    添加计划任务
    :param target: 任务目标执行函数对象
    :param in_time_dict: 配置时间详细
    :return:
    """
    print "monitor_3_develop: 配置一条任务!"
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
    command = """cat /etc/issue|grep -i "%s\"""" %host_obj.version
    ssh_stdin, ssh_stdout_basic, ssh_stderr = ssh.exec_command(command)
    # 判断系统版本
    if ssh_stdout_basic.read() is not None and len(ssh_stderr.read()) == 0:
        return True
    else:
        return False

class Task:
    def __init__(self, server_service_obj):
        self.server_service_obj = server_service_obj

    def genSchedule(self):
        """
        根据host_obj和db_obj和service_dict生成配置
        """
        project_nick = self.server_service_obj.project_nick
        host_obj = self.server_service_obj.host_obj
        db_obj = self.server_service_obj.db_obj
        service_dict = self.server_service_obj.service_dict

        # !注意: 需要保证配置数据库中命名与判断内容一致。
        # server
        if service_dict["m_type"] == 'system' and verifySystemVersion(host_obj):
            # centos
            if host_obj.version == 'centos':
                centos_monitor_server_obj = monitor_2_class.Centos_monitor_server(project_nick,host_obj,service_dict)
                # 1. cpu 监控
                if service_dict["m_dim"] == 'cpu-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_CPU, service_dict)
                # 2. disk 监控
                elif service_dict["m_dim"] == 'disk-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_disk, service_dict)
                # 3. IOPS 监控
                elif service_dict["m_dim"] == 'iops-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_IOPS, service_dict)
                # 4. memory 监控
                elif service_dict["m_dim"] == 'memory-usage':
                    runTaskByTimeType(centos_monitor_server_obj.check_memory, service_dict)
        # kettle
        elif service_dict["m_type"] == 'kettle':
            # 如果是kettle
            kettle_monitor_obj = monitor_2_class.Kettle_monitor(project_nick,host_obj,service_dict)

            if service_dict["m_dim"] == 'process':
                runTaskByTimeType(kettle_monitor_obj.check_process,service_dict)
        # gp
        elif service_dict["m_type"] == 'gp':
            gp_monitor_obj = monitor_2_class.GP_monitor(project_nick,host_obj,db_obj,service_dict)
            if service_dict["m_dim"] == 'connections-check':
                runTaskByTimeType(gp_monitor_obj.check_connections, service_dict)
            elif service_dict["m_dim"] == 'master-check':
                runTaskByTimeType(gp_monitor_obj.check_master, service_dict)
            elif service_dict["m_dim"] == 'segment-check':
                runTaskByTimeType(gp_monitor_obj.check_segment, service_dict)
        # newbi
        elif service_dict["m_type"] == 'newbi':
            newBI_monitor_obj = monitor_2_class.NewBI_monitor(project_nick,host_obj,service_dict)
            if service_dict["m_dim"] == 'process':
                runTaskByTimeType(newBI_monitor_obj.check_process, service_dict)
            elif service_dict["m_dim"] == 'login':
                runTaskByTimeType(newBI_monitor_obj.check_login, service_dict)
        else:
            raise ValueError('未知的服务！')



