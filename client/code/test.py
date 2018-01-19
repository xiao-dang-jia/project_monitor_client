#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 19/1/18
"""
function:

"""
import sys
import MySQLdb
import monitor_class

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')


host_ip = '172.18.21.196'
db_nick = '李宁配置数据库'
username = 'root'
password = '54321'
port = '5432'
database = 'mydata'

try:
    config_db_obj = monitor_class.DB(host_ip, db_nick, username, password, port, database)
    db = MySQLdb.connect(config_db_obj.host_ip, config_db_obj.username, config_db_obj.password, config_db_obj.database, charset='utf8')
    try:
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""show databasesdaa;""")
        result = cursor.fetchall()
        print result
    except MySQLdb.ProgrammingError as e:
        raise MySQLdb.ProgrammingError("ERROR 数据库执行语句出错:" + e)
    finally:
        db.close()
except MySQLdb.OperationalError as e:
    # raise MySQLdb.OperationalError("ERROR 数据库连接不上:" + str(e))
    print("ERROR 数据库连接不上:" + str(e))

