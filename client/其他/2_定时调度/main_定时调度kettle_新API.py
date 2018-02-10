#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""API更改后的代码:
1. 加入BlockingScheduler
2. 使用装饰器，而是用add_job
3. 在查询函数中调用SSH
当前版本:
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
import MySQLdb
import json
import abc
from abc import ABCMeta, abstractmethod
import paramiko
import traceback
import urllib,urllib2
import psycopg2
from apscheduler.schedulers.background import BlockingScheduler
import logging


#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig()
sched=BlockingScheduler()

## 获取配置信息
class Configure:
    """定义一个配置类"""
    def __init__(self,configure_file):
        """构造函数，输入一个配置文件路径"""
        self.configure_file = configure_file
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(configure_file)
        ## project_basic
        ### 获取项目基本信息

    def get_project_name(self):
        """获取project_name"""
        project_name = self.cf.get("project_basic","project_name")
        return project_name

    def get_hostlist(self):
        """获取主机，以列表形式返回"""
        host_list = self.cf.get("project_basic","host_list")
        host_list_arr = host_list.split(":")
        return host_list_arr

    def get_basic_by_host_ip(self,host_ip):
        """按照host_ip，获取主机basic_info:用户名+密码+版本"""
        host_basic = self.cf.get("project_basic", host_ip+"_basic")
        return host_basic

    def get_service_by_host_ip(self,host_ip):
        """按照host_ip，获取主机提供的service：部署的服务信息"""
        host_service = self.cf.get("project_basic", host_ip+"_service")
        host_service_arr = host_service.split(":")
        return host_service_arr

## 这步是否繁琐
    def get_username_by_basic_info(self,basic_info):
        """按照basic_info，返回一个username"""
        ## todo 检查是否可以简化
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[0]

    def get_passwd_by_basic_info(self,basic_info):
        """按照basic_info，返回一个passwd"""
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[1]

    def get_version_by_basic_info(self,basic_info):
        """按照basic_info，返回一个version"""
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[2]

### 获取服务的具体配置信息
    def get_configure_file_by_service(self,service_name):
        """根绝服务名字，返回一个配置列表"""
        service_option = self.cf.items(service_name)
        return service_option


### 获取服务监控参数
class Host:
    """定义一个主机类"""
    def __init__(self,host_ip,username,passwd,version):
        self.host_ip = host_ip
        self.username = username
        self.passwd = passwd
        self.version = version

    def __str__(self):
        return "Host:"+ str(self.host_ip) + "\tusername:"+ self.username + "\tpasswd:" + self.passwd + "\tversion:" + self.version

class Server_service:
    """服务器服务
    输入： host对象 + 服务（包括配置参数）
    输出：
    """
    def __init__(self, host_obj, service_dict):
        self.host_obj = host_obj
        self.service_dict = service_dict

    def __str__(self):
        return "Host:" + str(self.host_obj) + "\tThis is the service i provided:" + str(self.service_dict)

########################
#### 按照配置信息实施监控行为
class BaseMonitorAction:
    """监控类（抽象类）"""
    def __init__(self):
        self.type = ''

    @abstractmethod
    def run(self):
        """按照频率执行监控行为"""
        pass
#
## 服务器监控接口
class BaseServerMonitorable(object):
    """定义一个服务器基类"""
    __metaclass__ = ABCMeta  # 指定这是一个抽象类
    @abstractmethod
    def runCPU(self):
        """返回CPU信息"""
        pass

    @abstractmethod
    def runIOPS(self):
        """返回IOPS"""
        pass

    @abstractmethod
    def runMemory(self):
        """返回内存"""
        pass

    @abstractmethod
    def runDisk(self):
        """返回磁盘使用率"""
        pass

## centos 类
class Centos_monitor_server(BaseMonitorAction,BaseServerMonitorable):
    """继承自BaseServerMonitorable接口和基础监控类 BaseMonitorAction"""

    def __init__(self, host_obj, service_option):
        """这里给到的service_option要到最细的，即一个服务，一个对象进来"""
        BaseServerMonitorable.__init__(self)
        BaseMonitorAction.__init__(self)
        self.type = 'server_centos'
        self.host_obj = host_obj
        self.service_option = service_option

        # 增加自己的方法或者重写
    def runCPU(self,_ssh):
        """执行CPU监控"""
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command("""vmstat|awk 'NR==3 {print $13+$14"%"}'""")
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command("""vmstat""")
        data = format_json(project_name, self.host_obj.host_ip, self.type, 'use-CPU',ssh_stdout_basic.read(), ssh_stdout_log.read(), m_timestamp)
        urlPost(data)

    def runIOPS(self,_ssh):
        """执行IOPS"""
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command("""iostat |awk 'BEGIN{max=0} NR>6 {if($2+0>max+0) max=$2} END{print max"%"}'""")
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command("""iostat""")
        data = format_json(project_name, self.host_obj.host_ip, self.type, 'use-IOPS', ssh_stdout_basic.read(),ssh_stdout_log.read(), m_timestamp)
        urlPost(data)

    def runDisk(self,_ssh):
        """执行DISK监控"""
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command("""iostat -dx|awk 'BEGIN{max=0} {if($14+0>max+0) max=$14} END{print max"%"}'""")
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command("""iostat""")
        data = format_json(project_name, self.host_obj.host_ip, self.type, 'use-disk', ssh_stdout_basic.read(),ssh_stdout_log.read(), m_timestamp)
        urlPost(data)

    def runMemory(self,_ssh):
        """执行MEMORY监控，不RETRUN任何东西"""
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command("""vmstat|awk 'NR==3 {print $4/1024"MB"}'""")
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command("""vmstat""")
        data = format_json(project_name, self.host_obj.host_ip, self.type, 'use-memory', ssh_stdout_basic.read(), ssh_stdout_log.read(), m_timestamp)
        urlPost(data)


    def run(self):
        """传入得是服务器相关的监控项和频率"""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_obj.host_ip, username=self.host_obj.username, password=self.host_obj.passwd)
        ## 按照频率 进行监控
        # -todo 需要在此加入频率
        self.runMemory(ssh)
        self.runDisk(ssh)
        self.runCPU(ssh)
        self.runIOPS(ssh)
##
#
## 数据库相关监控
class GP_monitor(BaseMonitorAction):
    """GP相关监控"""
    def __init__(self,host_obj,service_option):
        BaseMonitorAction.__init__(self)
        self.type = 'gp-monitor'
        self.host_obj = host_obj
        self.service_option = service_option

    def fun_query(self,_conn,m_dim,query_m_value,query_m_log):
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cur = _conn.cursor()
        # m_value
        cur.execute(query_m_value)
        m_value = cur.fetchone()[0]

        # m_log
        cur.execute(query_m_log)
        query2_result = list(cur.fetchone())
        # eleminate None value
        query2_result = [str(x) for x in query2_result if x is not None]
        m_log = " ".join(query2_result)
        data = format_json(project_name, self.host_obj.host_ip, self.type, m_dim, m_value, m_log, m_timestamp)
        cur.close()
        return(data)


    def check_connections(self,_conn):
        """检查数据库连接数"""
        data = self.fun_query(_conn,'num-connections',"""select count(1) from pg_stat_activity;""","""select count(1) from pg_stat_activity;""")
        urlPost(data)


    def check_master(self,_conn):
        """检查数据库MASTER节点是否起着"""
        data = self.fun_query(_conn, 'master-status', """select case when status='u' then 'available' else 'fail' end as master状态 from gp_segment_configuration where content='-1' and role='p';""",
"""select * from gp_segment_configuration where content='-1' and role='p';""")
        urlPost(data)

    def check_segment(self,_conn):
        """检查数据库segment节点是否起着"""
        data = self.fun_query(_conn, 'segment-status', """select case when status='u' then 'available' else 'fail' end as segment状态 from gp_segment_configuration where content!='-1' and role='p';""",
"""select * from gp_segment_configuration where content!='-1' and role='p';""")
        urlPost(data)

    def run(self):
        print "GREENPLUM监控"
        conn = psycopg2.connect(database=service_option['database'], user=service_option['user'], password=service_option['password'], host=self.host_obj.host_ip, port=service_option['port'])
        ## -todo 加入监控频率
        self.check_connections(conn)
        self.check_master(conn)
        self.check_segment(conn)
        conn.close()

## newbi
# 1. newbi进程
# 2. 200
class NewBI_monitor(BaseMonitorAction):
    """NewBI相关监控"""
    def __init__(self, host_obj, service_option):
        BaseMonitorAction.__init__(self)
        self.type = 'newbi-monitor'
        self.host_obj = host_obj
        self.service_option = service_option

    def fun_query(self,_ssh,m_dim,query_m_value,query_m_log):
        """查询语句"""
        ## todo 抽象抽来 共同的方法
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command(query_m_value)
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command(query_m_log)
        data = format_json(project_name, self.host_obj.host_ip, self.type, m_dim,ssh_stdout_basic.read(), ssh_stdout_log.read(), m_timestamp)
        return data

    def check_process(self,_ssh):
        """查询newbi进程是否存在"""
        data = self.fun_query(_ssh, 'newbi-process', """ps -ef | grep jetty | grep -v "grep" | wc -l""", """ps -ef | grep jetty | grep -v 'grep'""")
        urlPost(data)

    def check_web_available(self,_ssh):
        """查询web是否可以访问"""
        # todo 模拟登陆
        pass

    def run(self):
        """执行"""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_obj.host_ip, username=self.host_obj.username, password=self.host_obj.passwd)
        ## 进行查询
        self.check_process(ssh)

class Kettle_monitor(BaseMonitorAction):
    """Kettle相关监控"""
    def __init__(self, host_obj, service_option):
        BaseMonitorAction.__init__(self)
        self.type = 'newbi-monitor'
        self.host_obj = host_obj
        self.service_option = service_option
        self.freq_process = 3

    def fun_query(self,_ssh,m_dim,query_m_value,query_m_log):
        """查询语句"""
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ssh_stdin, ssh_stdout_basic, ssh_stderr = _ssh.exec_command(query_m_value)
        ssh_stdin, ssh_stdout_log, ssh_stderr = _ssh.exec_command(query_m_log)
        data = format_json(project_name, self.host_obj.host_ip, None, self.type, m_dim, ssh_stdout_basic.read(),
                           ssh_stdout_log.read(), m_timestamp)
        print data
        return data

    # @sched.scheduled_job('interval', seconds=3, args=('self',))
    def check_process(self):
        """检查KETTLE进程是否存在"""
        ## 返回一个ssh对象
        _ssh = self.ssh_server()
        data = self.fun_query(_ssh,'kettle-process',"""ps -ef | grep spoon.sh | grep -v 'grep'|wc -l""","""ps -ef | grep spoon.sh | grep -v 'grep'""")
        urlPost(data)
        print "我在POST数据！！！！"

    def ssh_server(self):
        """ssh 连接到目标服务器中"""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_obj.host_ip, username=self.host_obj.username, password=self.host_obj.passwd)
        return ssh


    def run(self):
        """执行"""
        pass
        ## 进行查询
        # self.check_process(ssh)

class Task():
    """
    输入：server_service_obj
    输出：
    """
    def __init__(self,server_service_obj):
        self.server_service_obj = server_service_obj
        ## Server_service_obj 中有 host_obj + service_dict
        ## 传入的只会有一个host 但是会有多个service，那么得根据service来进行相应的操作

    def run(self):
        """在host_obj中，根据其不同的服务，执行监控任务"""
        ## 1. 先连入到服务器中
        ## 2. 根据服务列表，
        host_obj = self.server_service_obj.host_obj
        services = self.server_service_obj.service_dict
        print services
        for service in services:
            ### 服务大类
            if service =='system':
                # 具体到服务器版本 实例化Centos对象
                if host_obj.version == 'centos6.5':
                    pass
                ## 传入的是同一个服务的多个监控项
                    ## 执行监控
                    # print "服务CENTOS：" + str(services[service])
                    # Centos_monitor_server(host_obj,services[service]).run()
            elif service =='gp':
                pass
                # print "服务GP：" + str(services[service])
                # GP_monitor(host_obj,services[service]).run()
            elif service == 'newbi':
                pass
                # print "服务newbi：" + str(services[service])
                # NewBI_monitor(host_obj,services[service]).run()
            elif service == 'kettle':
                # 添加任务到sched 中去
                ## 判定使用的是时间还是频率
                if services[service]['time_format'] == 'period':
                    print int(services[service]['monitor_process'])
                    sched.add_job(Kettle_monitor(host_obj, services[service]).check_process, 'interval',
                                  seconds=int(services[service]['monitor_process']))
                elif services[service]['time_format'] == 'time':
                    # 先对时间做一次处理
                    # 取出时间
                    time = services[service]['monitor_process']
                    time_dict = getFormattedTime(time)
                    sched.add_job(Kettle_monitor(host_obj, services[service]).check_process, 'cron',
                                  year=time_dict['year'],month=time_dict['month'],day=time_dict['day'],
                                  hour=time_dict['hour'],minute=time_dict['minute'])
                print services[service]

def toDict(**kwargs):
    """
    格式化为字典
    :param kwargs:
    :return:
    """
    for key in kwargs.keys():
        globals()[key] = kwargs[key]
    return kwargs

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




def urlPost(postdata):
    """
    将API数据POST到服务端接口

    :param postdata:
    :return: 返回HTTP状态码
    """
    data = urllib.urlencode(postdata)
    req = urllib2.Request('http://172.18.21.245:8080/moniter/api/collect', data)
    response = urllib2.urlopen(req)
    return response.read()

def format_json(project_nick,host_nick,db_nick,m_type,m_dim,m_value,m_logger,m_timestamp):
    """
    将数据格式化API数据

    :param project_nick:
    :param host_nick:
    :param db_nick:
    :param m_type:
    :param m_dim:
    :param m_value:
    :param m_logger:
    :param m_timestamp:
    :return: 返回一个字典类型数据
    """
    data = {"project_nick":project_nick,\
            "host_nick":host_nick,\
            "db_nick":db_nick,\
            "m_type":m_type,\
            "m_dim":m_dim,\
            "m_value":m_value,\
            "m_logger":m_logger,\
            "m_timestamp":m_timestamp}
    return data

## 主方法
if __name__ == '__main__':
    try:
        ## 实例化一个配置文件
        configure_file = Configure('./configure.properties')
        host_list = configure_file.get_hostlist()
        server_service_obj_list = []
        project_name = configure_file.get_project_name()
        for i in range(len(configure_file.get_hostlist())):
            """为每一个主机创建一个主机对象"""

            # 获取用户名和密码 和版本
            basic_info = configure_file.get_basic_by_host_ip(host_list[i])
            username = configure_file.get_username_by_basic_info(basic_info)
            passwd = configure_file.get_passwd_by_basic_info(basic_info)
            version = configure_file.get_version_by_basic_info(basic_info)
            # 获取主机上部署的服务
            service_info = configure_file.get_service_by_host_ip(host_list[i])

            ## 将服务绑定给主机，创建一个服务器服务对象：有配置信息呢！
            host_obj = Host(host_list[i], username, passwd, version)

            # 根绝每台服务器的服务 获取配置
            service_dict = {}
            for service in service_info:
                service_option = configure_file.get_configure_file_by_service(service)
                service_option = dict((key, value) for key, value in service_option)
                # print service_option
                # print "^^^^^^^^^^^^^^^^^^^^^^^^"
                ## 字典
                service_dict[service] = service_option
            # print Server_service(host_obj, service_dict)
            ## 将该配置绑定到一个服务器服务对象上（包括其配置属性）: host对象 + service_option
            ### 每一个服务器对应到一个这样的对象
            ## 需要再分一次：
            server_service_obj_list.append(Server_service(host_obj, service_dict))

        task_list = []
        ## 根据Server_service列表生成任务对象
        for server_service_obj in server_service_obj_list:
            Task(server_service_obj).run()
        # 定时调度开启
        sched.start()
        print "+++++++++++++++++++++++++++++++++++++++finish+++++++++++++++++++++++++++++++++++++++"
    except Exception as e:
        exstr = traceback.format_exc()
        raise ValueError(exstr)
