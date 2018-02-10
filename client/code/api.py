#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 7/1/18
"""
function:
API模块
负责管理和服务端的API接口
"""
import sys
import urllib
import urllib2
import main
#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

def urlPost(postdata):
    """
    将API数据POST到服务端接口

    :param postdata:
    :return: 返回HTTP状态码
    """
    url = main.API_URL
    data = urllib.urlencode(postdata)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    if response.read() == 'OK':
        print "成功POST数据：" + str(postdata)
    return response.read()

def format_json(project_nick,host_nick,db_nick,m_type,m_dim,m_value,m_logger,m_timestamp):
    """
    将数据格式化API数据

    :param project_nick:
    :param host_nick:
    :param db_nick:
    :param m_type:
    :param m_dim:
    :param m_value:
    :param m_logger:
    :param m_timestamp:
    :return: 返回一个字典类型数据
    """
    data = {"project_nick": project_nick,
            "host_nick": host_nick,
            "db_nick": db_nick,
            "m_type": m_type,
            "m_dim": m_dim,
            "m_value": m_value,
            "m_logger": m_logger,
            "m_timestamp": m_timestamp}
    return data
