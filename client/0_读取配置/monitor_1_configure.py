#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:

"""
import sys
import MySQLdb
import json
import monitor_2_class

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

## 中文
class CCode:
    """
    python中文打印元组，列表，字典
    """
    def str(self, content, encoding='utf-8'):
        # 只支持json格式
        # indent 表示缩进空格数
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)
        # pass
#     pass

def trans(input_text):
    """
    转换为中文
    :param input_text:
    :return:
    """
    cCode = CCode()
    return cCode.str(input_text)

def getData(db_obj,table,column="*",conditions=''):
    """
    从数据库中获取数据

    :param db_obj: 目标数据库对象
    :param table: 来源表
    :param column: select的列
    :param conditions: 筛选条件
    :return:
    """
    db = MySQLdb.connect(db_obj.host_ip,db_obj.username,db_obj.password,db_obj.database,charset='utf8')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""select %s from %s%s;""" %(column,table,conditions))
    # print """select %s from %s%s;""" %(column,table,conditions)
    result = cursor.fetchall()
    db.close()
    return result

def getHostByProjectnick(config_db_obj,in_project_nick):
    """
    通过项目名称 从数据库中获取相应的主机IP列表
    :param in_project_nick:
    :return:
    """
    project_nick_conditions = " where project_nick='%s'" % in_project_nick
    data_host = getData(db_obj=config_db_obj, table='moniter_m_d_host', conditions=project_nick_conditions)
    hostip_list = []
    for row in data_host:
        # print row
        # host_nick = row['host_nick']
        host_ip = row['host']
        hostip_list.append(host_ip)
    return hostip_list

class MDHostDetail:
    def __init__(self,project_nick,config_db_obj):
        self.project_nick = project_nick
        self.config_db_obj = config_db_obj

    def __get_host_nick_list(self):
        """
        通过项目获取该项目的服务器ip
        :return:
        """
        project_nick_conditions = " where project_nick='%s'" % self.project_nick
        data_host = getData(db_obj=self.config_db_obj, table='moniter_m_d_host', conditions=project_nick_conditions)
        host_nick_list = []
        for row in data_host:
            # print row
            # host_nick = row['host_nick']
            host_ip = row['host_nick']
            host_nick_list.append(host_ip)
        return host_nick_list

    def get_host_object_by_host_nick(self, host_nick):
        """
        通过host_nick + project_nick 从表moniter_m_d_host 和 表moniter_m_d_user_host获取其相关的信息
        :return:
        """
        project_nick_conditions = " where project_nick='%s' and host_nick='%s'" % (self.project_nick, host_nick)
        rows_f_m_d_host = getData(db_obj=self.config_db_obj, table='moniter_m_d_host',
                                  conditions=project_nick_conditions)
        rows_f_m_d_user_host = getData(db_obj=self.config_db_obj, table='moniter_m_d_user_host',
                                       conditions=project_nick_conditions)
        # 虽然只会有一行
        for row in rows_f_m_d_host:
            host_ip = row['host']
            host_port = row['host']
            server_type = row['server_type']

        for row in rows_f_m_d_user_host:
            username = row['username']
            password = row['password']

        host_object = monitor_2_class.Host(host_ip, host_nick, username, passwd=password, version=server_type)
        return host_object

    def get_host_object_list(self):
        """
        返回host对象列表
        :return:
        """
        host_nick_list = self.__get_host_nick_list()
        host_object_list = []
        for host_nick in host_nick_list:
            host_object_list.append(self.get_host_object_by_host_nick(host_nick))
        return host_object_list


    def get_db_dict_by_host_nick(self,db_nick):

        db_dict_conditions = " where project_nick='%s' and db_nick='%s'" % (self.project_nick, db_nick)
        print('---')
        rows_f_m_d_db = getData(db_obj=self.config_db_obj, table='moniter_m_d_db',
                                  conditions=db_dict_conditions)
        # self.host_ip = host_ip
        # self.db_nick = db_nick
        # self.username = username
        # self.password = password
        # self.port = port
        # self.database = database
        monitor_2_class.DB(rows_f_m_d_db['host'],rows_f_m_d_db['db_nick'],rows_f_m_d_db['host'])

    def get_service_dict_by_host_nick(self,host_nick):
        """
        返回该host_nick所具备的服务列表，每个列表元素为一个字典
        :param host_nick:
        :return:
        """
        project_checklist_condition = " where m_status='on' and project_nick='%s' and host_nick='%s'" % (self.project_nick,host_nick)
        rows_f_m_project_checklist = getData(db_obj=self.config_db_obj, table='moniter_m_project_checklist', conditions=project_checklist_condition)

        m_dim_dict_list = []
        for row in rows_f_m_project_checklist:
            m_dim_dict = {}
            if row['m_type'] == 'gp':
                # 需要加入数据库配置
                print('我要生成gp对象')
                self.get_db_dict_by_host_nick(row['db_nick'])
                db_detail = None
            else:
                db_detail = None

            m_type = row['m_type']
            m_dim = row['m_dim']
            m_interval_type = row['m_interval_type']
            m_interval_time = row['m_interval_time']
            m_dim_dict = {'db_detail':db_detail,'m_type':m_type, 'm_dim':m_dim, 'm_interval_type':m_interval_type, 'm_interval_time':m_interval_time}
            m_dim_dict_list.append(m_dim_dict)
        return m_dim_dict_list


def genConfigure():
    host_ip = '172.18.21.245'
    db_nick = '李宁配置数据库'
    username = 'root'
    password = '54321'
    port = '5432'
    database = 'mydata'

    config_db_obj = monitor_2_class.DB(host_ip, db_nick, username, password, port, database)
    # 1. 获取项目信息 project_nick
    data_project = getData(db_obj=config_db_obj,table='moniter_m_project')
    ## 获取信息
    # print data_project
    for row in data_project:
        project_nick = row['nick']

    # 2. 实例化一个项目host表对象
    md_host_detail_obj = MDHostDetail(project_nick,config_db_obj)
    # 2.1 按照项目名称，获取主机host_obj的列表
    host_object_list = md_host_detail_obj.get_host_object_list()

    # 3. 按照项目名称 和 host_object 获取主机对应的监控项目，以字典的形式返回
    task_list = []
    for host_object in host_object_list:
        m_dim_dict_list = md_host_detail_obj.get_service_dict_by_host_nick(host_object.host_nick)
        # 按照里面的服务生成相应的任务
        for m_dim_dict in m_dim_dict_list:
            # 生成一个单一的任务，每一个任务相当于checklist中的一行
            task_list.append(monitor_2_class.Server_service(host_object,m_dim_dict))

    # 有了task_list
    # for task in task_list:
    #     print task.service_dict

genConfigure()