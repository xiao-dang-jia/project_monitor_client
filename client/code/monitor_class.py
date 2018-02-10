#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:
这个模块定义了监控类及其实现方法
"""
import sys
from abc import ABCMeta, abstractmethod
import time
import paramiko
import psycopg2
import api

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

class Host:
    """主机类"""
    def __init__(self,host_ip, host_nick, username, password, version):
        self.host_ip = host_ip
        self.host_nick = host_nick
        self.username = username
        self.password = password
        self.version = version

    def __str__(self):
        return "Host:" + str(self.host_ip) + "\tusername:" + self.username + "\tpassword:" + self.password + "\tversion:" + self.version

class DB:
    """数据库类"""
    def __init__(self,host_ip,db_nick, username, password, port, database):
        self.host_ip = host_ip
        self.db_nick = db_nick
        self.username = username
        self.password = password
        self.port = port
        self.database = database

    def __str__(self):
        return "host_ip:" + str(
            self.host_ip) + "\tusername:" + self.username + "\tpassword:" + self.password + "\tdb_nick:" + self.db_nick

## 公共函数
def ssh_server(host_obj):
    """
    ssh 连接到目标服务器中
    :param host_obj:
    :return: 返回ssh对象
    """
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_obj.host_ip, username=host_obj.username, password=host_obj.password)
    return ssh

def fun_query(ssh,query_m_value,query_m_log):
    """
    执行ssh 返回查询值结果和查询日志结果
    :param ssh: ssh目标对象
    :param m_dim: 侦测维度
    :param query_m_value: 查询结果的语句
    :param query_m_log: 查询日志的语句
    :return: 返回(查询的监控值, 监控日志, 查询时间) (tuple)
    """
    m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print m_timestamp
    ssh_stdin, ssh_stdout_basic, ssh_stderr = ssh.exec_command(query_m_value)
    ssh_stdin, ssh_stdout_log, ssh_stderr = ssh.exec_command(query_m_log)
    return ssh_stdout_basic.read(), ssh_stdout_log.read(), m_timestamp

class Server_service:
    """服务器服务"""
    def __init__(self, project_nick, host_obj, db_obj, service_dict):
        self.project_nick = project_nick
        self.host_obj = host_obj
        self.db_obj = db_obj
        self.service_dict = service_dict

    def __str__(self):
        return "Host:" + str(self.host_obj) + "\tThis is the service i provided:" + str(self.service_dict)

# class BaseMonitorAction:
#     """监控类（抽象类）所有监控类都要override这个类中的方法和属性"""
#     def __init__(self):
#         self.project_nick = ''
#         self.host_obj = None
#         self.service_dict = {}

    # @abstractmethod
    # def run(self):
    #     pass

class Kettle_monitor:
    """Kettle相关监控"""
    # todo 感觉概念不分离：理想中Kettle_monitor应该只管监控行为，不需要service_dict
    def __init__(self, project_nick, host_obj, service_dict):
        """
        :param project_nick: 为了指定返回数据中的 project_nick
        :param host_obj: 为了生成ssh的对象
        :param service_dict: 为了指定返回数据中的m_type, m_dim
        """
        # BaseMonitorAction.__init__(self)
        self.project_nick = project_nick
        self.host_obj = host_obj
        self.service_dict = service_dict

    def check_process(self):
        """
        检查KETTLE进程是否存在
        1. 创建ssh 对象
        2. 在目标服务器上执行命令
        3. post数据
        :return:
        """
        # 1. 生成ssh对象
        ssh = ssh_server(self.host_obj)
        # 2. 查询数据
        query_result = fun_query(ssh, """ps -ef | grep spoon.sh | grep -v 'grep'|wc -l""", """ps -ef | grep spoon.sh | grep -v 'grep'""")
        # 3. 格式化数据
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'],
                               self.service_dict['m_dim'], query_result[0], query_result[1], query_result[2])
        # 4. 向接口中post数据
        api.urlPost(data)

## 服务器监控接口
class BaseServerMonitorable(object):
    """定义一个服务器基类"""

    # 指定这是一个抽象类
    __metaclass__ = ABCMeta

    # 定义了服务器监控所需要的方法
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
class Centos_monitor_server(BaseServerMonitorable):
    """继承自BaseServerMonitorable接口和基础监控类 BaseMonitorAction"""

    def __init__(self, project_nick, host_obj, service_dict):
        """
        :param host_obj:
        """
        BaseServerMonitorable.__init__(self)
        # BaseMonitorAction.__init__(self)
        self.project_nick = project_nick
        self.host_obj = host_obj
        self.service_dict = service_dict

    def check_CPU(self):
        """检查CPU"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,"""vmstat|awk 'NR==3 {print ($13+$14)/100}'""","""vmstat""")
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'], self.service_dict['m_dim'],
                               query_result[0], query_result[1], query_result[2])
        api.urlPost(data)

    def check_IOPS(self):
        """检查IOPS"""
        ssh = ssh_server(self.host_obj)
        # 最大的一个iops
        query_result = fun_query(ssh,"""iostat |awk 'BEGIN{max=0} NR>6 {if($2+0>max+0) max=$2} END{print max}'""","""iostat""")
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'], self.service_dict['m_dim'],
                               query_result[0], query_result[1], query_result[2])
        api.urlPost(data)

    def check_disk(self):
        """检查DISK"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,"""iostat -dx|awk 'BEGIN{max=0} {if($14+0>max+0) max=$14} END{print max/100}'""","""iostat""")
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'], self.service_dict['m_dim'],
                               query_result[0], query_result[1], query_result[2])
        api.urlPost(data)

    def check_memory(self):
        """检查MEMORY"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,"""vmstat|awk 'NR==3 {print $4/1024"MB"}'""","""vmstat""")
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'], self.service_dict['m_dim'],
                               query_result[0], query_result[1], query_result[2])
        api.urlPost(data)

class NewBI_monitor():
    """NewBI相关监控"""
    def __init__(self, project_nick, host_obj, service_dict):
        # BaseMonitorAction.__init__(self)
        self.project_nick = project_nick
        self.host_obj = host_obj
        self.service_dict = service_dict

    def check_process(self):
        """检查newbi进程"""
        ssh = ssh_server(self.host_obj)
        query_result = fun_query(ssh,"""ps -ef | grep jetty | grep -v "grep" | wc -l""","""ps -ef | grep jetty | grep -v 'grep'""")
        data = api.format_json(self.project_nick, self.host_obj.host_nick, None, self.service_dict['m_type'], self.service_dict['m_dim'],
                               query_result[0], query_result[1], query_result[2])
        api.urlPost(data)

    def check_login(self,_ssh):
        """查询web是否可以访问"""
        # todo 模拟登陆
        pass

def db_connection(db_object):
    """
    连接数据库
    :param db_object:
    :return: 返回数据库连接对象
    """
    conn = psycopg2.connect(database=db_object.database, user=db_object.username,
                            password=db_object.password, host=db_object.host_ip,
                            port=db_object.port)
    return conn

class GP_monitor():
    """GP相关监控"""
    def __init__(self, project_nick, host_obj, db_object, service_dict):
        # BaseMonitorAction.__init__(self)
        self.project_nick = project_nick
        self.host_obj = host_obj
        self.db_object = db_object
        self.service_dict = service_dict

    def db_fun_query(self, query_m_value, query_m_log):
        """
        执行数据库系统表查询
        :param query_m_value: 查询监控值的sql语句
        :param query_m_log: 查询监控日志的sql语句
        :return: 返回查询结果
        """
        conn = db_connection(self.db_object)
        try:
            cur = conn.cursor()
        except Exception as e:
            conn.close()
            raise ValueError("ERROR 数据库连接异常:" + str(e))
        try:
            m_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # m_value
            cur.execute(query_m_value)
            m_value = cur.fetchone()[0]
            # m_log
            print query_m_log
            cur.execute(query_m_log)
            # 对数据做处理
            query2_result_org = cur.fetchone()

            # 乳沟查询数据为空，记录查询语句
            if query2_result_org is None:
                m_log = query_m_log
            else:
                query2_result = list(query2_result_org)

                # 将查询结果连接起来，方便日志记录
                # eleminate None value
                query2_result = [str(x) for x in query2_result if x is not None]
                m_log = " ".join(query2_result)
            data = api.format_json(self.project_nick, self.host_obj.host_nick, self.db_object.db_nick,
                                   self.service_dict['m_type'], self.service_dict['m_dim'], m_value, m_log, m_timestamp)
            return data
        except Exception as e:
            raise ValueError("ERROR 数据库操作异常:" + str(e))
        finally:
            """确保connection关闭"""
            cur.close()
            conn.close()

    def check_connections(self):
        """检查数据库连接数"""
        data = self.db_fun_query("""select count(1) from pg_stat_activity;""","""select count(1) from pg_stat_activity;""")
        api.urlPost(data)

    def check_master(self):
        """
        检查数据库MASTER节点是否起着
        1. content='-1' 代表master节点，否则为segment节点
        2. role='p' 代表当前角色为primary
        """
        data = self.db_fun_query("""select status from gp_segment_configuration where content='-1' and role='p';""",
                                 """select * from gp_segment_configuration where content='-1' and role='p';""")
        api.urlPost(data)

    def check_segment(self):
        """检查数据库segment节点是否起着"""
        data = self.db_fun_query("""select status from gp_segment_configuration where content!='-1' and role='p';""",
                                 """select * from gp_segment_configuration where content!='-1' and role='p';""")
        api.urlPost(data)

    def check_overtime_sql(self):
        """检查超时sql，返回超时SQL数量"""
        data = self.db_fun_query("""SELECT count(1) FROM pg_stat_activity WHERE current_query != '<IDLE>' AND
current_query NOT ILIKE '%pg_stat_activity%' AND age(clock_timestamp(),query_start)>= '2 hours'::interval;"""
                                 ,"""SELECT procpid,query_start,age(clock_timestamp(),query_start),usename,current_query FROM pg_stat_activity
WHERE current_query != '<IDLE>' AND current_query NOT ILIKE '%pg_stat_activity%' AND age(clock_timestamp(),query_start)
>= '2 hours'::interval ORDER BY query_start desc;""")
        api.urlPost(data)

# 数据逻辑监控类
class DataLogic():
    pass
