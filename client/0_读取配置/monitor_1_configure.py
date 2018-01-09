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
    通过项目名称 从数据库中获取相应的主机名
    :param in_project_nick:
    :return:
    """
    project_nick_conditions = " where project_nick='%s'" % in_project_nick
    try:
        data_host = getData(db_obj=config_db_obj, table='moniter_m_d_host', conditions=project_nick_conditions)
    except Exception as e:
        raise ValueError("找不到")
    for row in data_host:
        print row
        host_nick = row['host_nick']
        host_ip = row['host']
        print host_nick
        print host_ip

def genConfigure():
    host_ip = '172.18.21.245'
    db_nick = '李宁配置数据库'
    username = 'root'
    password = '54321'
    port = '5432'
    database = 'mydata'

    config_db_obj = monitor_2_class.DB(host_ip, db_nick, username, password, port, database)
    # 1. 获取项目信息
    data_project = getData(db_obj=config_db_obj,table='moniter_m_project')
    ## 获取信息
    # print data_project
    for row in data_project:
        project_nick = row['nick']
        print project_nick

    # 2. 按照项目名称，获取主机信息
    getHostByProjectnick(config_db_obj,project_nick)
    #
    # project_nick_conditions = " where project_nick='%s'" %project_nick
    # data_host = getData(db_obj=config_db_obj,table='moniter_m_d_host',conditions=project_nick_conditions)
    # for row in data_host:
    #     print row
    #     host_nick = row['host_nick']
    #     host_ip =
    #     # 3.1 通过host_nick找到相应的host，生成相应的host_obj。
    #     host_nick = row[2]
    #     host_ip = row[3]
    #     host_port = row[4]
    #     server_type = row[5]
    #     user_conditions = " where project_nick= '%s' and host_nick = '%s'" %(project_nick,host_nick)
    #     data_user = getData(db_obj=config_db_obj,table='moniter_m_d_user_host',conditions=user_conditions)
    #     print data_user
    #     host_username =data_user[0][4]
    #     host_password =data_user[0][5]
    #     # 生成一个host实例
    #     host_obj = monitor_2_class.Host(host_ip,host_nick,host_username,host_password,server_type)
    #
    #     # todo
    #     #
    #     db_user_conditions = " where project_nick= '%s' and host = '%s'" % (project_nick, host_ip)
    #     data_db_user = getData(db_obj=config_db_obj, table='moniter_m_d_db', conditions=db_user_conditions)
    #     # 1. 如果有数据再做处理，无数据就置为空。
    #     if len(data_db_user)!=0:
    #         # 实例化db对象
    #         # todo 明天这里开始做
    #         monitor_2_class.DB(host_ip,)
    #     else:
    #         pass
    #     # 2. 如果同一个IP上有多个数据库要监控的话，那么还需要再加一层判断
    #
    #     # db_nick =
    #     # database =
    #     print data_user


        # 3.2 通过host_nick和project_nick找到相应的服务，监控项和监控频率

        # 4. 将其封装为server_service_obj，成为一个list。

    # print data_host


    # 3. 根据ip获取相应的服务

genConfigure()