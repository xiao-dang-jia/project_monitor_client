#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/1/18
"""
function:

"""
import sys

#解决 二进制str 转 unicode问题
reload(sys)
sys.setdefaultencoding('utf8')


def toDict(**kwargs):
    """
    格式化为字典
    :param kwargs:
    :return:
    """
    for key in kwargs.keys():
        globals()[key] = kwargs[key]
    return kwargs

def getFormattedTime(in_time_str):
    try:
        time_str_arr = in_time_str.split(' ')

        date_str = time_str_arr[0]
        time_str = time_str_arr[1]
        # 处理日期

        out_year = date_str.split('-')[0]
        out_month = date_str.split('-')[1]
        out_day = date_str.split('-')[2]

        out_hour = time_str.split(':')[0]
        out_minute = time_str.split(':')[1]
        return toDict(out_year=out_year, out_month=out_month, out_day=out_day, out_hour=out_hour, out_minute=out_minute)
    except Exception as e:
        raise TypeError('执行时间配置错误!%s' %e)

if __name__ == '__main__':
    try:
        print(getFormattedTime('2018-01-05 15:30'))


    except Exception, e:
        print e