#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import time

SEP_ASTERISK= "********************"
logger = logging.getLogger('script_logger')

filename_suffix = time.strftime("%Y%m%d", time.localtime())
filename_script_log_detail = './test_detail.log_detail_' + filename_suffix
filename_script_log_warning = './test_detail.log_warning_' + filename_suffix

hdlr_detail = logging.FileHandler(filename_script_log_detail)
hdlr_warning = logging.FileHandler(filename_script_log_warning)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr_detail.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

#
#
# logging.basicConfig(filename=filename_script_log, mode='w',level=logging.DEBUG,format='%(asctime)s %(message)s')
#
# for i in range(4):
#         look = '这是第一个循环内执行的命令：'
#         leap = 'psql -h 127.0.0.1'
#         logging.debug('%s %s', look, leap)
#         logging.debug(SEP_ASTERISK)
#         logging.debug(SEP_ASTERISK*2 + "hello")
#
# for i in range(5):
#     look = '这是第二个循环内执行的命令：'
#     leap = 'psql -h 127.0.0.1'
#     logging.warn('[ERRdasdaOR]: %s %s', look, leap)


import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

def main():
    setup_logger('log1', r'./log1.log')
    setup_logger('log2', r'./log2.log')
    log1 = logging.getLogger('log1')
    log2 = logging.getLogger('log2')

    log1.info('Info for log 1!')
    log2.info('Info for log 2!')
    log1.error('Oh, no! Something went wrong!')

if '__main__' == __name__:
    main()


    # logger = logging.getLogger(__name__)