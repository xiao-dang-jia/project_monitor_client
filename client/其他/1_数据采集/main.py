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
# import MySQLdb
import json
import abc
from abc import ABCMeta, abstractmethod
# import common.CommandLine as COMMAND
import paramiko
import traceback
import urllib,urllib2

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

def urlPost(postdata):
  data = urllib.urlencode(postdata)
  req = urllib2.Request('http://172.18.21.245:8080/moniter/api/collect', data)
  response = urllib2.urlopen(req)
  return response.read()


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

    def get_hostlist(self):
        """获取主机，以列表形式返回"""
        host_list = self.cf.get("project_basic","host_list")
        host_list_arr = host_list.split(":")
        return host_list_arr

    def get_basic_by_host_ip(self,host_ip):
        """按照host_ip，获取主机basic_info"""
        host_basic = self.cf.get("project_basic", host_ip+"_basic")
        return host_basic

    def get_service_by_host_ip(self,host_ip):
        """按照host_ip，获取主机提供的service"""
        host_service = self.cf.get("project_basic", host_ip+"_service")
        host_service_arr = host_service.split(":")
        return host_service_arr

## 这步是否繁琐
    def get_username_by_basic_info(self,basic_info):
        """按照basic_info返回一个username"""
        ## todo 检查是否可以简化
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[0]

    def get_passwd_by_basic_info(self,basic_info):
        """按照basic_info返回一个passwd"""
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[1]

    def get_version_by_basic_info(self,basic_info):
        """按照basic_info返回一个version"""
        basic_info_arr = basic_info.split(":")
        return basic_info_arr[2]


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
    """服务器服务"""
    def __init__(self,host_obj,service):
        self.host_obj = host_obj
        self.service = service

    def __str__(self):
        return "Host:" + str(self.host_obj) + "\tThis is the service i provided:" + str(self.service)


# ##### 建立连接
# class Connection(metaclass=ABCMeta):
#     """连接类"""
#     pass
#
#
# #### 获取日志

class Monitor_action(object):
    """所有监控行为的抽象类"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.type = ''

    @abstractmethod
    def run_monitor(self):
        pass

# ## 服务器监控接口
class ServerMonitorable(abc.ABCMeta):
    """定义一个服务器基类"""
    @abstractmethod
    def getCPU(self):
        """返回CPU信息"""
        pass

    @abstractmethod
    def getIOPS(self):
        """返回IOPS"""
        pass

    @abstractmethod
    def getMemory(self):
        """返回内存"""
        pass

    @abstractmethod
    def getDisk(self):
        """返回磁盘使用率"""
        pass


## centos 类
class Centos_monitor_server(ServerMonitorable,Monitor_action):
    """继承自ServerMonitorable接口"""
    def __init__(self, host_obj):
        # locals()
        ServerMonitorable.__init__(self)
        Monitor_action.__init__(self)
        self.type = 'server_centos'
        self.host_obj = host_obj

    def __new__(cls, *args, **kwargs):
        return Monitor_action.__new__(cls,host_obj)

        # 增加自己的方法或者重写
    def getCPU(self):
        """返回CPU使用率"""
        command = """vmstat|awk 'NR==3 {print $13+$14"%"}'"""
        # print(command)
        # result = os.popen(command).readlines()
        # return result
        return command

    def getIOPS(self):
        """返回IOPS"""
        command = """ll"""
        return command

    def getMemory(self):
        """返回内存"""
        command = """vmstat|awk 'NR==3 {print $4/1024"MB"}'"""
        return command

    def getDisk(self):
        """返回磁盘使用率"""
        command = """iostat -dx|awk 'BEGIN{max=0} {if($14+0>max+0) max=$14} END{print max"%"}'"""
        return command

    def run_monitor(self):
        print('!!!!')
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host_obj.host_ip, username=self.host_obj.username, password=self.host_obj.passwd)
        ## 获取服务器磁盘
        print("xxxx")
        ## 调整监控频率
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(Centos_monitor_server.getDisk())
        print ssh_stdout.readlines()

class Monitortask_per_host:
    """定义一个监控任务类，要执行登陆，监控"""

    def __init__(self, m_host_obj,m_service_list,m_freq):
        """服务器对象，监控类别，监控项，监控参数 没想好"""
        ## 主机名，用户名，密码，版本
        self.m_host_obj = m_host_obj
        ## service列表
        self.m_service_list = m_service_list
        self.m_freq = m_freq

    def run_task_per_service(self,service):
        """每一个服务的任务，比如说"""
        # 如果是某个service 就跑某个服务

    ## 每一个服务会有一个 Monitortask_host
    def run_monitortask(self):
        ## 首先进行SSH
        # ssh = paramiko.SSHClient()
        # ssh.load_system_host_keys()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(self.m_host.host_ip, username=self.m_host.username, password=self.m_host.passwd)
        ## 创建监控对象
        # 对服务器上的每个服务执行相应的操作
        for m_serivce in self.m_service_list:
            # 将该服务实例化
            print m_serivce
            if m_serivce == 'system':
                ## 用多态去
                ## 执行监控
                print '++++++++++++++++++++++++++++++++++++'
                # Centos_monitor_server.__new__(self.m_host_obj)
                # Centos_monitor_server(self.m_host_obj)
        # 比方说一个服务监控服务
        # ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls -l')
        # print ssh_stdout.readlines()
#
# ## 数据库日志类
# class Database(metaclass=ABCMeta):
#     """定义一个数据库基类"""
#
#     @abstractmethod
#     def getData(self):
#         """返回数据库查询结果信息"""
#         pass
#
# ## 文本日志类
# class Text(metaclass=ABCMeta):
#     """定义一个文本基类"""
#
#     @abstractmethod
#     def getData(self):
#         """返回错误信息"""
#         pass
#
# #### 公共方法
def format_json(project_nick,server_ip,m_type,m_dim,m_value,m_logger,m_timestamp):
    """返回一个JSON类型数据"""
    data = {"project_nick":project_nick,\
            "server_ip":server_ip,\
            "m_type":m_type,\
            "m_dim":m_dim,\
            "m_value":m_value,\
            "m_logger":m_logger,\
            "m_timestamp":m_timestamp}
    data_json = json.dumps(data)
    # print(type(data_json))
    return data


# 模块2： newbi 监控

# 模块3： greenplum 监控

# 模块4： kettle 监控

# API
# def insert_real_data(project_nick,m_type,m_dim,m_value,m_logger,m_timestamp):
#     """将API数据插入服务器中"""
#     cur = conn_monitor.cursor()
#     try:
#         cur.execute("select * from monitor.m_project_checklist;")
#         cur.execute('insert into Login values("%s", "%s", "%s", "%s", "%s", "%s")' \
#                     % (project_nick, m_type, m_dim, m_value, m_logger, m_timestamp))
#         conn_monitor.commit()
#     except Exception as e:
#         conn_monitor.rollback()
#         ## 抛出数据库插入异常
#         raise ValueError(e)
## 主方法
if __name__ == '__main__':
    try:
        ## 实例化一个配置文件
        configure_file = Configure('./configure.properties')
        print('hostlist:')
        host_list = configure_file.get_hostlist()
        Server_obj_list = []
        Server_service_obj_list = []
        for i in range(len(configure_file.get_hostlist())):
            """为每一个主机创建一个主机对象"""
            basic_info = configure_file.get_basic_by_host_ip(host_list[i])
            username = configure_file.get_username_by_basic_info(basic_info)
            passwd = configure_file.get_passwd_by_basic_info(basic_info)
            version = configure_file.get_version_by_basic_info(basic_info)

            service_info = configure_file.get_service_by_host_ip(host_list[i])
            # 将 服务绑定到每个主机上
            ### 创建主机对象
            host_obj = Host(host_list[i],username,passwd,version)
            print host_obj
            Server_service_obj_list.append(Server_service(host_obj,service_info))
        ## 根据每一个服务器对象和其提供的服务 分别创建任务
        print("------------------------")
        for server_service_obj in Server_service_obj_list:
            print server_service_obj
            ## 传入进来一个服务器地址，版本以及所需要监控的多个服务，每个服务有个频率
            task_per_host = Monitortask_per_host(server_service_obj.host_obj, server_service_obj.service, m_freq=0)
            task_per_host.run_monitortask()
            break

        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print m_timestamp
        # post_data = format_json('lining-dw','172.18.21.197','server', 'cpu-use', '20%', 'Test', m_timestamp)
        # post_data1 = format_json('lining-dw','172.18.21.197','server', 'memeroy-use', '32169004KB', 'Test', m_timestamp)
        # post_data2 = format_json('lining-dw','172.18.21.197','server', 'disk-use', '30%', 'Test', m_timestamp)
        # post_data3 = format_json('lining-dw','172.18.21.197','server', 'IOPS', '200', 'Test', m_timestamp)
        # post_data4 = format_json('lining-dw','172.18.21.197','newbi', 'proc-newbi', '1c', 'Test', m_timestamp)
        # post_data5 = format_json('lining-dw','172.18.21.197','newbi', 'web-newbi', '200', 'Test', m_timestamp)


        post_data12 = format_json('opple','172.18.21.117','server', 'memeroy-use', '129004KB', 'Test', m_timestamp)
        # post_data22 = format_json('opple','172.18.21.117','servenr', 'disk-use', '2%', 'Test', m_timestamp)
        # post_data32 = format_json('opple','172.18.21.117','server', 'IOPS', '100', 'Test', m_timestamp)
        # post_data42 = format_json('opple','172.18.21.117','newbi', 'proc-newbi', '1c', 'Test', m_timestamp)
        # post_data52 = format_json('opple','172.18.21.117','newbi', 'web-newbi', '200', 'Test', m_timestamp)
        urlPost(post_data12)
        # urlPost(post_data22)
        # urlPost(post_data32)
        # urlPost(post_data42)
        # urlPost(post_data52)
        # urlPost(post_data1)
        # urlPost(post_data2)
        # urlPost(post_data3)
        # urlPost(post_data4)
        # urlPost(post_data5)
    except Exception as e:
        # print(locals())
        exstr = traceback.format_exc()
        raise ValueError(exstr)
