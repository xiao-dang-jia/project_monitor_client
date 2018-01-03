#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time
import sys
import os
import string
import time
import datetime
from optparse import OptionParser
import ConfigParser
# import MySQLdb
import json
import abc
from abc import ABCMeta, abstractmethod
# import common.CommandLine as COMMAND
import paramiko
import traceback
import urllib,urllib2
import psycopg2
import psycopg2.extensions

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')

class GP_monitor():
    """GP相关监控"""
    def __init__(self):
        pass

    def check_connections(self,_conn):
        """检查数据库连接数"""
        cur = _conn.cursor()
        query = """select count(1) from pg_stat_activity;"""
        cur.execute(query)
        print str(cur.fetchone()[0])

    def check_master(self,_conn):
        """检查数据库MASTER节点是否起着"""
        cur = _conn.cursor()
        query = """select case when status='u' then 'available' else 'fail' end as master状态 from gp_segment_configuration where content='-1' and role='p';"""
        cur.execute(query)
        print str(cur.fetchone()[0])
        print "++++++++++++++++++++++++++++++++++++++++"
        query2 = """select * from gp_segment_configuration where content='-1' and role='p';"""


        print "+++++++++++++++++++++++++++++++++++++++"

    def run(self):
        print "GREENPLUM监控"
        conn = psycopg2.connect(database="postgres", user="gpadmin", password="gpadmin", host="172.18.21.179", port="5432")
        conn.set_client_encoding('utf-8')
        # self.check_connections(conn)
        self.check_master(conn)

if __name__ == '__main__':
    GP_monitor().run()