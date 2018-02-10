#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 18/1/18
"""
function:
初始化配置表中的Next_checktime


"""
import sys
import MySQLdb
import monitor_class
import datetime

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')


def initialise_next_checktime(current_time, config_db_obj, server_service_obj):
    """
    初始化monitor_m_project_checklist中的next_checktime，以第一次发送监控时间为值。
    :param server_service_obj:
    :return:
    """
    db = MySQLdb.connect(config_db_obj.host_ip, config_db_obj.username, config_db_obj.password, config_db_obj.database,
                         charset='utf8')
    cursor = db.cursor()

    project_nick = server_service_obj.project_nick
    host_nick = server_service_obj.host_obj.host_nick
    m_type = server_service_obj.service_dict['m_type']
    m_dim = server_service_obj.service_dict['m_dim']
    # 有的监控项 没有db_obj对象
    if server_service_obj.db_obj is not None:
        db_nick = server_service_obj.db_obj.db_nick
        conditions = "where project_nick='%s' and host_nick='%s' and db_nick='%s' and m_type='%s' and m_dim='%s'" % (
            project_nick, host_nick, db_nick, m_type, m_dim)
    else:
        conditions = "where project_nick='%s' and host_nick='%s' and db_nick is null and m_type='%s' and m_dim='%s'" % (
            project_nick, host_nick, m_type, m_dim)

    # 时间是不一样的
    if server_service_obj.service_dict['m_interval_type'] == 'period':
        timedelta = server_service_obj.service_dict['m_interval_time']
        next_checktime = current_time + datetime.timedelta(seconds=int(timedelta))
        print "initilisation.py: next_checktime:" + str(next_checktime)
    elif server_service_obj.service_dict['m_interval_type'] == 'everyday':
        # 1. 获取凌晨时间
        today = datetime.datetime.today()
        wee_hour = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        # 2. 时间间隔
        timedelta = server_service_obj.service_dict['m_interval_time']
        # 3. 初始化的checktime
        next_checktime = wee_hour + datetime.timedelta(seconds=int(timedelta))
        print "initilisation.py: next_checktime:" + str(next_checktime)
    else:
        raise ValueError('ERROR initilisation.py: 未知的m_interval_type类型!')
    try:
        # 执行sql语句
        cursor.execute(
            """update monitor_m_project_checklist set Next_checktime='%s' %s;""" % (next_checktime, conditions))
        # 提交到数据库执行
        db.commit()
    except MySQLdb.Error as e:
        # Rollback in case there is any error
        db.rollback()
        raise
    finally:
        cursor.close()
        db.close()


