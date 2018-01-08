#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:

"""
import sys
import abc
from abc import ABCMeta, abstractmethod
import time
import paramiko
import psycopg2

import monitor_4_post





#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')


PROJECT_NICK = 'lining-dw'



# 公共函数
def ssh_server(host_obj):
    """
    ssh 连接到目标服务器中
    :param host_obj:
    :return: 返回ssh对象
    """
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_obj.host_ip, username=host_obj.username, password=host_obj.passwd)
    return ssh


def fun_query(ssh,m_dim,query_m_value,query_m_log):
    """
    执行 ssh命令返回查询结果和日志结果
    :param self:
    :param ssh: ssh目标对象
    :param m_dim: 侦测维度
    :param query_m_value: 查询结果的语句
    :param query_m_log: 查询日志的语句
    :return: 一个
    """
    m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print m_timestamp
    ssh_stdin, ssh_stdout_basic, ssh_stderr = ssh.exec_command(query_m_value)
    ssh_stdin, ssh_stdout_log, ssh_stderr = ssh.exec_command(query_m_log)
    return (ssh_stdout_basic.read(),ssh_stdout_log.read(),m_timestamp)

### 获取服务监控参数
class Host:
    """定义一个主机类"""
    def __init__(self,host_ip,host_nick,username,passwd,version):
        self.host_ip = host_ip
        self.host_nick = host_nick
        self.username = username
        self.passwd = passwd
        self.version = version

    def __str__(self):
        return "Host:"+ str(self.host_ip) + "\tusername:"+ self.username + "\tpasswd:" + self.passwd + "\tversion:" + self.version


class DB:
    """定义了个数据库类"""
    def __init__(self,host_ip,db_nick, username, password, port, database):
        self.host_ip = host_ip
        self.db_nick = db_nick
        self.username = username
        self.password = password
        self.port = port
        self.database = database

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


class BaseMonitorAction:
    """监控类（抽象类）"""
    def __init__(self):
        self.type = ''

    # @abstractmethod
    # def run(self):
    #     """按照频率执行监控行为"""
    #     pass

class Kettle_monitor(BaseMonitorAction):
    """Kettle相关监控"""
    def __init__(self, host_obj):
        BaseMonitorAction.__init__(self)
        self.type = 'kettle'
        self.host_obj = host_obj

    def check_process(self):
        """
        检查KETTLE进程是否存在
        1. 创建ssh 对象
        2. 在目标服务器上执行命令
        3. post数据
        :return:
        """
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'kettle-process',"""ps -ef | grep spoon.sh | grep -v 'grep'|wc -l""","""ps -ef | grep spoon.sh | grep -v 'grep'""")
        m_dim = 'process'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim, query_result[0],query_result[1],query_result[2])
        monitor_4_post.urlPost(data)

## 服务器监控接口
class BaseServerMonitorable(object):
    """定义一个服务器基类"""
    __metaclass__ = ABCMeta  # 指定这是一个抽象类
    @abstractmethod
    def check_CPU(self):
        """返回CPU信息"""
        pass

    @abstractmethod
    def check_IOPS(self):
        """返回IOPS"""
        pass

    @abstractmethod
    def check_memory(self):
        """返回内存"""
        pass

    @abstractmethod
    def check_disk(self):
        """返回磁盘使用率"""
        pass

## centos 类
class Centos_monitor_server(BaseMonitorAction,BaseServerMonitorable):
    """继承自BaseServerMonitorable接口和基础监控类 BaseMonitorAction"""

    def __init__(self, host_obj):
        """
        :param host_obj:
        """
        BaseServerMonitorable.__init__(self)
        BaseMonitorAction.__init__(self)
        self.type = 'system'
        self.host_obj = host_obj

        # 增加自己的方法或者重写
    def check_CPU(self):
        """执行CPU监控"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'use-CPU',"""vmstat|awk 'NR==3 {print $13+$14"%"}'""","""vmstat""")
        m_dim = 'cpu-usage'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim,
                                          query_result[0], query_result[1], query_result[2])
        monitor_4_post.urlPost(data)

    def check_IOPS(self):
        """执行IOPS"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'use-IOPS',"""iostat |awk 'BEGIN{max=0} NR>6 {if($2+0>max+0) max=$2} END{print max"%"}'""","""iostat""")
        m_dim = 'IOPS-usage'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim,
                                          query_result[0], query_result[1], query_result[2])
        monitor_4_post.urlPost(data)

    def check_disk(self):
        """执行DISK监控"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'use-disk',"""iostat -dx|awk 'BEGIN{max=0} {if($14+0>max+0) max=$14} END{print max"%"}'""","""iostat""")
        m_dim = 'disk-usage'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim,
                                          query_result[0], query_result[1], query_result[2])
        monitor_4_post.urlPost(data)

    def check_memory(self):
        """执行MEMORY监控"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'use-memory',"""vmstat|awk 'NR==3 {print $4/1024"MB"}'""","""vmstat""")
        m_dim = 'memory-usage'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim,
                                          query_result[0], query_result[1], query_result[2])
        monitor_4_post.urlPost(data)

class NewBI_monitor(BaseMonitorAction):
    """NewBI相关监控"""
    def __init__(self, host_obj):
        BaseMonitorAction.__init__(self)
        self.type = 'newbi'
        self.host_obj = host_obj

    def check_process(self):
        """查询newbi进程是否存在"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,'process',"""ps -ef | grep jetty | grep -v "grep" | wc -l""","""ps -ef | grep jetty | grep -v 'grep'""")
        m_dim = 'process'
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick, None, self.type, m_dim,
                                          query_result[0], query_result[1], query_result[2])
        monitor_4_post.urlPost(data)

    def check_login(self,_ssh):
        """查询web是否可以访问"""
        # todo 模拟登陆
        pass

def db_connection(db_object):
    """
    连接数据库
    :param db_object:
    :return:
    """
    conn = psycopg2.connect(database=db_object.database, user=db_object.username,
                            password=db_object.password, host=db_object.host_ip,
                            port=db_object.port)
    conn.close()
    return conn

class GP_monitor(BaseMonitorAction):
    """GP相关监控"""
    def __init__(self,host_obj,db_object):
        BaseMonitorAction.__init__(self)
        self.type = 'gp'
        self.host_obj = host_obj
        self.db_object = db_object

    def fun_query(self,conn,m_dim,query_m_value,query_m_log):
        print("执行gp查询中")
        m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cur = conn.cursor()
        # m_value
        cur.execute(query_m_value)
        m_value = cur.fetchone()[0]

        # m_log
        cur.execute(query_m_log)
        query2_result = list(cur.fetchone())
        # eleminate None value
        query2_result = [str(x) for x in query2_result if x is not None]
        m_log = " ".join(query2_result)
        data = monitor_4_post.format_json(PROJECT_NICK, self.host_obj.host_nick,self.db_object.db_nick, self.type, m_dim, m_value, m_log, m_timestamp)
        cur.close()
        return(data)


    def check_connections(self):
        """检查数据库连接数"""
        conn = db_connection(self.host_obj)
        data = self.fun_query(conn,'check-connections',"""select count(1) from pg_stat_activity;""","""select count(1) from pg_stat_activity;""")
        monitor_4_post.urlPost(data)


    def check_master(self):
        """检查数据库MASTER节点是否起着"""
        conn = db_connection(self.host_obj)
        data = self.fun_query(conn, 'master-status', """select case when status='u' then 'available' else 'fail' end as master状态 from gp_segment_configuration where content='-1' and role='p';""",
"""select * from gp_segment_configuration where content='-1' and role='p';""")
        monitor_4_post.urlPost(data)

    def check_segment(self):
        """检查数据库segment节点是否起着"""
        conn = db_connection(self.host_obj)
        data = self.fun_query(conn, 'segment-status', """select case when status='u' then 'available' else 'fail' end as segment状态 from gp_segment_configuration where content!='-1' and role='p';""",
"""select * from gp_segment_configuration where content!='-1' and role='p';""")
        monitor_4_post.urlPost(data)

