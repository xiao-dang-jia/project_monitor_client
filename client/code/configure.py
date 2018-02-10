#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:
从配置数据库中读取配置，生成 server_service_obj_list，供monitor_3_develop生成任务。

 * server_service_obj_list 由四部分生成：project_nick + host_obj主机对象 + db_obj对象 + server_service_dict字典
 ** project_nick 项目昵称
 ** host_obj 会具备一个host所具备的属性
 ** db_obj 具备数据库所具备的属性
 ** server_service_dict 是这个主机上的监控项配置字典。如：{"m_type":"system", "m_dim":"cpu-check", "time_interval_type":"period", "":""}
 ** 总结：三者组成了最细的一个任务，配置到 apscheduler中。
"""
import sys
import MySQLdb
import monitor_class

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

def getData(db_obj,table,column="*",conditions=''):
    """
    从数据库中获取数据

    :param db_obj: 目标数据库对象
    :param table: 来源表
    :param column: select的列
    :param conditions: 筛选条件
    :return: 返回查询的数据 (dictionary形式)
    """
    try:
        db = MySQLdb.connect(db_obj.host_ip, db_obj.username, db_obj.password, db_obj.database, charset='utf8')
        try:
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""select %s from %s%s;""" % (column, table, conditions))
            print("""select %s from %s%s;""" % (column, table, conditions))
            result = cursor.fetchall()
            return result
        except MySQLdb.ProgrammingError as e:
            raise MySQLdb.ProgrammingError("ERROR 数据库执行语句出错:" + str(e))
            #raise MySQLdb.ProgrammingError("ERROR 数据库执行语句出错:" + e)
        finally:
            # 一定关闭数据库连接
            db.close()
    except MySQLdb.OperationalError as e:
        raise MySQLdb.OperationalError("ERROR 数据库连接不上:" + str(e))

class M_D_HOST:
    """为M_D_HOST表建立了一个类，可以获取这种表所需的信息"""
    def __init__(self,config_db_obj,project_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick

    def __get_host_nick_list(self):
        """
        通过项目昵称，获取M_D_HOST表中的项目昵称列表
        :return: 昵称列表 (list)
        """
        project_nick_conditions = " where project_nick='%s'" % self.project_nick
        rows = getData(db_obj=self.config_db_obj, table='monitor_m_d_host', conditions=project_nick_conditions)
        host_nick_list = []
        for row in rows:
            host_ip = row['host_nick']
            host_nick_list.append(host_ip)
        return host_nick_list

    def get_hostip_by_hostnick(self,host_nick):
        """
        通过host_nick获取host_ip
        :param host_nick:
        :return:
        """
        condition = " where project_nick='%s' and host_nick='%s'" % (self.project_nick, host_nick)
        rows = getData(db_obj=self.config_db_obj, table='monitor_m_d_host',
                                  conditions=condition)
        if len(rows) != 1:
            raise ValueError("ERROR: 一个host_nick + project_nick的联合主键对应到了多个host_ip！")
        return rows[0]['host']

    def get_host_object_by_host_nick(self, host_nick):
        """
        通过host_nick + project_nick 从表monitor_m_d_host 和 表monitor_m_d_user_host获取其相关的信息，生成host_obj
        :param host_nick:
        :return: host_obj (Host类对象)
        """
        project_nick_conditions = " where project_nick='%s' and host_nick='%s'" % (self.project_nick, host_nick)
        rows_host = getData(db_obj=self.config_db_obj, table='monitor_m_d_host',
                                  conditions=project_nick_conditions)

        rows_host_user = getData(db_obj=self.config_db_obj, table='monitor_m_d_user_host',
                                       conditions=project_nick_conditions)

        for row in rows_host:
            host_ip = row['host']
            server_type = row['server_type']

        for row in rows_host_user:
            username = row['username']
            password = row['password']
	host_object = monitor_class.Host(host_ip, host_nick, username, password=password, version=server_type)
	return host_object

    def get_host_object_list(self):
        """
        返回 host_obj 列表
        :return: host_obj_list (list)
        """
        host_nick_list = self.__get_host_nick_list()
        host_object_list = []

        for host_nick in host_nick_list:
            host_object_list.append(self.get_host_object_by_host_nick(host_nick))
        return host_object_list

class M_D_DB:
    """M_D_DB表"""
    def __init__(self, project_nick, config_db_obj, host_nick, db_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick
        self.host_nick = host_nick
        self.db_nick = db_nick

    def get_db_object(self):
        """
        通过 db_nick + project_nick + host_nick 生成 db_obj
        :return: db_obj
        """
        conditions = " where project_nick='%s' and db_nick='%s' and host_nick='%s'" % (self.project_nick, self.db_nick, self.host_nick)
        rows = getData(self.config_db_obj, table='monitor_m_d_db', conditions=conditions)
        print(rows)

        if len(rows) != 1:
            raise ValueError("ERROR: 一个host_nick + project_nick + db_nick的联合主键对应到了多个database！")

        host_table_obj=M_D_HOST(self.config_db_obj, self.project_nick)
        host_ip = host_table_obj.get_hostip_by_hostnick(host_nick=self.host_nick)

        user_dict = self.get_db_user_dict()

        db_obj = monitor_class.DB(host_ip=host_ip, db_nick=self.db_nick, username=user_dict['username'],
                                  password=user_dict['password'], port=rows[0]["port"], database=rows[0]['db_name'])
        return db_obj

    def get_db_user_dict(self):
        """
        通过 project_nick + db_nick 获取db的用户的信息
        :return:
        """
        condition = " where project_nick='%s' and db_nick='%s'" % (self.project_nick, self.db_nick)
        rows = getData(self.config_db_obj, table='monitor_m_d_user_db', conditions=condition)
        return rows[0]

class M_PROJECT_CHECKLIST:
    """M_PROJECT_CHECKLIST配置表相关"""

    def __init__(self, config_db_obj, project_nick, host_nick):
        self.config_db_obj = config_db_obj
        self.project_nick = project_nick
        self.host_nick = host_nick

    def get_service_dict_list(self):
        """
        返回监控项的列表
        :return: m_dim_dict_list (list)
        """
        project_checklist_condition = " where m_status='on' and project_nick='%s' and host_nick='%s'" % (
                self.project_nick, self.host_nick)

        rows = getData(db_obj=self.config_db_obj, table='monitor_m_project_checklist', conditions=project_checklist_condition)
        m_dim_dict_list = []

        for row in rows:
            m_dim_dict = {'db_nick':row['db_nick'], 'm_type':row['m_type'], 'm_dim':row['m_dim'],
                          'm_interval_type':row['m_interval_type'], 'm_interval_time':row['m_interval_time']}
            m_dim_dict_list.append(m_dim_dict)
        return m_dim_dict_list

def gen_server_service_obj_list(config_db_obj):
    """
    返回任务的列表
    :param host_ip:
    :param db_nick:
    :param username:
    :param password:
    :param port:
    :param database:
    :return: server_service_obj_list
    """
    # 初始化配置数据库连接
    # 1. 获取项目信息 project_nick
    # todo 是否这样能完全确定一个项目
    # 服务器端需要多个nick确定一个项目
    data_project = getData(db_obj=config_db_obj, table='monitor_m_project', conditions=" where nick='爱哆哆'")
    # 标准客户端
    # data_project = getData(db_obj=config_db_obj, table='monitor_m_project')
    for row in data_project:
        project_nick = row['nick']
    m_d_host_obj = M_D_HOST(config_db_obj=config_db_obj, project_nick=project_nick)
    server_service_obj_list = []
    # 2. 获取该项目拥有的主机
    for host_obj in m_d_host_obj.get_host_object_list():
        # 2.1 获取该host的监控项配置字典
        m_project_checklist_obj = M_PROJECT_CHECKLIST(config_db_obj=config_db_obj, project_nick=project_nick, host_nick=host_obj.host_nick)
        # 2.2
        # A: 生成db_obj
        # B: 将任务字典统一存放到server_service_obj_list中去
        for service_dict in m_project_checklist_obj.get_service_dict_list():

            # 如果该服务需要数据库对象支持，那么生成db_object。否则置为None
            if service_dict['db_nick'] is not None:
                db_obj = M_D_DB(project_nick=project_nick, config_db_obj=config_db_obj, host_nick=host_obj.host_nick,
                                db_nick=service_dict['db_nick']).get_db_object()
            else:
                db_obj = None
            #2.3 生成单个server_service_obj
            server_service_obj = monitor_class.Server_service(project_nick=project_nick, host_obj=host_obj, db_obj=db_obj, service_dict=service_dict)
            server_service_obj_list.append(server_service_obj)
    print "configure: 生成项目配置信息完毕!"
    return server_service_obj_list
