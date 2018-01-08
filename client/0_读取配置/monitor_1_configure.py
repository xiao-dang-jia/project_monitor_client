#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:

"""
import sys
import MySQLdb
import json

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

def getConfigure(configure_hostip,configure_username,configure_password,configure_database):
    """
    按照项目名称和版本，读取所需要的配置信息
    从数据库中取出服务配置信息

    :param hostip:
    :param username:
    :param password:
    :param database:
    :param table:
    :return: 返回一个元组
    """
    db = MySQLdb.connect(configure_hostip,configure_username,configure_password,configure_database,charset='utf8')
    cursor = db.cursor()
    table = "c_monitor_one_table"
    cursor.execute("""select * from %s where status is True;""" %table)
    result = cursor.fetchall()
    db.close()
    return result

def getHostobjByIP(input_ip):
    pass