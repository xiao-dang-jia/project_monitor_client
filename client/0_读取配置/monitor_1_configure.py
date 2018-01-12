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

class M_D_HOST:
    def __init__(self,config_db_obj,project_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick


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

    def get_hostip_by_hostnick(self,host_nick):
        condition = " where project_nick='%s' and host_nick='%s'" % (self.project_nick, host_nick)
        # print condition
        rows = getData(db_obj=self.config_db_obj, table='moniter_m_d_host',
                                  conditions=condition)
        if len(rows)!=1:
            raise ValueError("ERROR: 一个host_nick + project_nick的联合主键对应到了多个host_ip！")
        return rows[0]['host']

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

class M_D_DB:
    def __init__(self,project_nick,config_db_obj,host_nick,db_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick
        self.host_nick = host_nick
        self.db_nick = db_nick

    def get_db_object(self):
        """按照db_nick + project_nick + host_nick 获取 db_obj"""
        db_dict_conditions = " where project_nick='%s' and db_nick='%s' and host_nick='%s'" % (self.project_nick, self.db_nick, self.host_nick)
        rows = getData(self.config_db_obj, table = 'moniter_m_d_db', conditions= db_dict_conditions)

        if len(rows)!=1:
            raise ValueError("ERROR: 一个host_nick + project_nick + db_nick的联合主键对应到了多个database！")

        host_table_obj = M_D_HOST(self.config_db_obj,self.project_nick)
        host_ip = host_table_obj.get_hostip_by_hostnick(host_nick=self.host_nick)

        user_dict = self.get_db_user_dict()

        db_obj = monitor_2_class.DB(host_ip=host_ip,db_nick=self.db_nick,username=user_dict['username'],
                                    password=user_dict['password'],port=rows[0]["port"],database=rows[0]['db_name'])
        return db_obj

    def get_db_user_dict(self):
        condition = " where project_nick='%s' and db_nick='%s'" % (self.project_nick,self.db_nick)
        rows = getData(self.config_db_obj, table='moniter_m_d_user_db', conditions=condition)
        return rows[0]

class M_PROJECT_CHECKLIST:
    def __init__(self, config_db_obj, project_nick, host_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick
        self.host_nick = host_nick
        # self.db_nick = db_nick

    def get_service_dict_list(self):
        """
        返回服务的列表
        :param host_nick:
        :return:
        """
        project_checklist_condition = " where m_status='on' and project_nick='%s' and host_nick='%s'" % (
                self.project_nick,self.host_nick)

        rows = getData(db_obj=self.config_db_obj, table='moniter_m_project_checklist', conditions=project_checklist_condition)
        m_dim_dict_list = []
        for row in rows:
            m_dim_dict = {'db_nick':row['db_nick'],'m_type':row['m_type'], 'm_dim':row['m_dim'], 'm_interval_type':row['m_interval_type'], 'm_interval_time':row['m_interval_time']}
            m_dim_dict_list.append(m_dim_dict)
        return m_dim_dict_list

def gen_server_service_obj_list(host_ip = '172.18.21.245',db_nick = '李宁配置数据库',username = 'root',password = '54321',port = '5432',database = 'mydata'):
    """return 任务列表"""
    config_db_obj = monitor_2_class.DB(host_ip, db_nick, username, password, port, database)
    # 1. 获取项目信息 project_nick
    data_project = getData(db_obj=config_db_obj,table='moniter_m_project')
    ## 获取信息
    # print data_project
    for row in data_project:
        project_nick = row['nick']

    m_d_host_obj = M_D_HOST(config_db_obj=config_db_obj,project_nick=project_nick)


    server_service_obj_list = []
    ## 将组合起来生成相应的 Server_sevice
    for host_obj in m_d_host_obj.get_host_object_list():
        # 获取该host_nick + project_nick 的服务项目
        m_project_checklist_obj = M_PROJECT_CHECKLIST(config_db_obj=config_db_obj, project_nick=project_nick, host_nick=host_obj.host_nick)
        # 配置到一个任务列表中去

        for service_dict in m_project_checklist_obj.get_service_dict_list():
            #### db_object
            #如果服务类型是gp那么找到gp对象，那么生成db_object。否则置为None
            if service_dict['db_nick'] is not None:
                db_obj = M_D_DB(project_nick=project_nick, config_db_obj=config_db_obj, host_nick=host_obj.host_nick,
                                db_nick=service_dict['db_nick']).get_db_object()
            else:
                db_obj = None
            #### 单个service
            server_service_obj = monitor_2_class.Server_service(host_obj=host_obj, db_obj=db_obj, service_dict=service_dict)

            server_service_obj_list.append(server_service_obj)
    return server_service_obj_list