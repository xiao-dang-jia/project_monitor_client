import pymysql.cursors
import datetime,time
import logging 
import re
logging.basicConfig(filename='test.log', format='%(asctime)s %(message)s',level=logging.DEBUG)
def check_real_report(curtime,delta):
	connection = pymysql.connect(host='localhost',
				user='root',
				password='54321',
				db='mydata',
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
	logging.info("\n\n*监控扫描开始执行")
	with connection.cursor() as cursor:
		'''
		记录当前时间，确定扫描real记录的范围	
		'''	
		curday = datetime.date.today()
		logging.info('本次检查的当前时间:'+str(curtime))
		earliest_time = curtime - delta 
		logging.info('本次检查涵盖的最早时间：'+str(earliest_time))
		sql = "SELECT * FROM moniter_m_d_real WHERE timestamp_v >=  %s\
		AND timestamp_v <= %s"
		cursor.execute(sql, (earliest_time,curtime))
		#搜素出所有指定的real记录对象
		results = cursor.fetchall()
		if len(results) == 0:
			logging.info('未发现可供检查的数据')
		else:
			logging.info('发现带检查记录'+ str(len(results))+'条')
			#将real记录逐条与监控阀值进行匹配，若匹配到，则根据监控阀值的各项设置进行检查判定，去生成相关记录	
			for result in results:
				try:
					sql = "SELECT * FROM moniter_m_project_checklist WHERE project_nick = %s AND host_nick = %s AND db_nick = %s AND m_type = %s AND m_status = 'on'"
					cursor.execute(sql, (str(result['project_nick']),str(result['host_nick']),str(result['db_nick']),str(result['m_type'])))
					logging.info("正在监控的数据是：")
					for k,v in result.items():
						logging.info(k + ' : ' + str(v))
					#查找出该监控数据所匹配的监控阀值
					result_check = cursor.fetchone()
					if result_check is None:
						logging.info("未匹配到任何监控项")
						continue
					#检查到该监控阀值为首次调用(Next_checktime==None)，则初始化其Next_checktime值为当前时间
					if result_check['Next_checktime'] is None:
						logging.info('Next_checktime为空，执行初始化')
						result_check['Next_checktime'] = curtime - datetime.timedelta(minutes = result_check['m_interval_time']/60) 
						logging.info('初始化完成，Next_checktime：%s',str(result_check['Next_checktime']))
					#用于report入库参考阀值时间
					curNext_checktime =  result_check['Next_checktime'] 
					#根据监控阀值时间类型，选择阀值时间判定分支,并更新下一次监控阀值的时间Next_checktime
					m_interval_time_type_dict = {'everyday':m_interval_time_type_everyday,'period':m_interval_time_period}
					m_interval_time_type_dict_return = m_interval_time_type_dict.get(result_check['m_interval_type'])(result,result_check)
					logging.info('m_interval_time_type_dict_return:'+str(m_interval_time_type_dict_return))
					#返回更新后的该条监控阀值的下次时间
					Next_checktime = m_interval_time_type_dict_return[1]
					if m_interval_time_type_dict_return[0] is None:
						logging.info('不满足监控阀值的时间要求，该条监控数据被忽略')
						continue
					#根据监控阀值数值判定类型，选择运算分支	
					m_value_type_dict = {'等于':m_value_type_e,'大于':m_value_type_g,'小于':m_value_type_l,'大于等于':m_value_type_ge,'小于等于':m_value_type_le,'区间':m_value_type_interval}
					m_value_type_dict_return = m_value_type_dict.get(result_check['m_value_type'])(result,result_check)
					m_status = m_value_type_dict_return
					#调用告警发送,返回发送状态
					m_send_status = "未发送"

					#调用告警发送,返回发送状态
					if m_status == 'error':
						logging.info("需要发送告警信息")
						pass
					else:
						pass 	
					m_send_status = "未发送"
					for k,v in result.items():
						logging.info(k + ' : ' + str(v))
					sql = "INSERT INTO moniter_m_report (project_nick,host_nick,db_nick,m_date,m_timestamp,m_type,m_dim,m_value,m_status,m_send_status,description,timestamp_v)	VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					cursor.execute(sql, (result['project_nick'],\
						result['host_nick'],result['db_nick'],curday,curNext_checktime,result['m_type'],result['m_dim'],result['m_value'],m_status,m_send_status,result['m_logger'],result['timestamp_v']
						))
					connection.commit()
					logging.info('监控报告生成')
					#更新数据库中监控阀值的下次告警时间
					if Next_checktime == result_check['Next_checktime']:
						pass
					else:
						sql = "UPDATE  moniter_m_project_checklist SET Next_checktime = %s WHERE id = %s"
						cursor.execute(sql,(Next_checktime,result_check['id']))
						connection.commit()			
				except ZeroDivisionError as error:
					logging.info('错误'+ str(error))
	connection.close()
#m_interval_time_type_everyday
'''
1.监控阀值的时间类型为everyday每天,则检查该监控数据的客户端时间m_timestamp和入库时间timestamp_v位于监控阀值的时间点Next_checktime附近(+,-).若满足则该条监控数据有效
2.监控阀值的时间点Next_checktime的附近范围大小是由监控阀值的监控间隔时间m_interval_time(*2,+,-)决定的，若为空值，则默认为5分钟
'''
def m_interval_time_type_everyday():
	list = [None,result_check['Next_checktime']]
	if result_check['m_interval_time'] == None:
		minutes = 5
	#Next_checktime_delta = datetime.timedelta(minutes = result_check['m_interval_time']/60)
	Next_checktime_delta = datetime.timedelta(minutes = minutes)
	if result['m_timestamp'] >= (result_check['Next_checktime'] - Next_checktime_delta) and result['m_timestamp'] <= (result_check['Next_checktime'] + Next_checktime_delta):
		if result['timestamp_v'] >= (result_check['Next_checktime'] - Next_checktime_delta) and result['m_timestamp'] <= (result_check['Next_checktime'] + Next_checktime_delta):
			list[0] = 'True'
	return list		
#m_interval_time_period
'''
1.监控阀值的时间类型为period时间间隔,则检查该监控数据的客户端时间m_timestamp和入库时间timestamp_v位于监控阀值的时间点Next_checktime附近(+,).若满足则该条监控数据有效
2.监控阀值的时间点Next_checktime的附近范围大小是由监控阀值的监控间隔时间m_interval_time(*1,+,)决定的，若为空值，则默认为5分钟
'''
def m_interval_time_period(result,result_check):
	list = [None,result_check['Next_checktime']]
	minutes = 5
	#Next_checktime_delta = datetime.timedelta(minutes = result_check['m_interval_time']/60)
	Next_checktime_delta = datetime.timedelta(minutes = minutes) 
	if result['m_timestamp'] >= (result_check['Next_checktime'] - Next_checktime_delta)  and result['m_timestamp'] <= (result_check['Next_checktime'] + Next_checktime_delta):
		if result['timestamp_v'] >= (result_check['Next_checktime'] - Next_checktime_delta)  and result['m_timestamp'] <= (result_check['Next_checktime'] + Next_checktime_delta):
			list[0] = 'True'
			list[1] = result_check['Next_checktime'] + Next_checktime_delta
	return list
#m_value_type=='等于'
def m_value_type_e(result,result_check):
	m_status = 'success' if result['m_value'] == result_check['m_value'] else  'error'
	return m_status

#m_value_type=='大于'		
def m_value_type_g(result,result_check):
	result_check_m_value = re.match(r'(\d*)(\w*)',result_check['m_value']).group(1)
	result_m_value = re.match(r'(\d*)(\w*)',['m_value']).group(1)
	m_status = 'success' if int(result_m_value) > int(result_check_m_value) else 'error'
	return m_status

#m_value_type=='小于'
def m_value_type_l(result,result_check):
	result_check_m_value = re.match(r'(\d*)(\w*)',result_check['m_value']).group(1)
	result_m_value = re.match(r'(\d*)(\w*)',result['m_value']).group(1)
	m_status = 'success' if int(result_m_value) < int(result_check_m_value)  else 'error'
	return m_status

#m_value_type=='大于等于'
def m_value_type_ge(result,result_check):
	result_check_m_value = re.match(r'(\d*)(\w*)',result_check['m_value']).group(1)
	result_m_value = re.match(r'(\d*)(\w*)',['m_value']).group(1)
	m_status = 'success' if int(result_m_value) >= int(result_check_m_value) else 'error'
	return m_status

#m_value_type=='小于等于'
def m_value_type_le(result,result_check):
	result_check_m_value = re.match(r'(\d*)(\w*)',result_check['m_value']).group(1)
	result_m_value = re.match(r'(\d*)(\w*)',['m_value']).group(1)
	m_status = 'success' if int(result_m_value) <= int(result_check_m_value) else 'error'		
	return m_status
#m_value_type=='区间'
def m_value_type_interval(result,result_check):
	value_type = re.match(r'(\d+)(,)(\d+)',str(result_check['m_value']))
	min_value = int(value_type.group(1))
	max_value = int(value_type.group(3))	
	m_status = 'success' if min_value <= int(result['m_value']) and int(result['m_value']) <= max_value else 'error'

#检测未按时收到数据的监控告警
def auto_update_Nexttime(curtime,delta):
	logging.info('监控时间校正开始')
	connection = pymysql.connect(host='localhost',
		user='root',
		password='54321',
		db='mydata',
		charset='utf8mb4',
		cursorclass=pymysql.cursors.DictCursor)
	sql = "SELECT * FROM moniter_m_project_checklist WHERE m_interval_type = %s and m_status = 'on' and Next_checktime is not null "
	with connection.cursor() as cursor:
		cursor.execute(sql,'period')
		check_lists = cursor.fetchall()
		if check_lists is None:
			logging.info('没有找到任何监控阀值数据')
		else:
			logging.info('发现阀值记录'+str(len(check_lists))+'条')
			count = 0
			for check_detail in check_lists:
				if check_detail['Next_checktime'] > curtime:
					logging.info('该监控阀值时间超前，不做处理')
					continue
				elif check_detail['Next_checktime'] + delta >= curtime:
					logging.info('该监控阀值时间正常待更新，不做处理')
					continue
				else:
					count += 1
					logging.info('该监控阀值时间已逾期，需要进行时间校正,并发出空告警')
					logging.info('该监控信息是:' + str(check_detail))
					logging.info('该监控阀值的当前时间:' + str(check_detail['Next_checktime']))
					Next_checktime = check_detail['Next_checktime']	
					#计算监控阀值最新时间，并记录未收到的告警条数N
					N = 0	
					delta_period = datetime.timedelta(seconds = check_detail['m_interval_time'])
					while Next_checktime + delta < curtime:
						N +=1
						Next_checktime = N * delta_period + check_detail['Next_checktime']
					#更新监控阀值时间
					sql = 'UPDATE moniter_m_project_checklist SET Next_checktime = %s  WHERE id = %s'
					cursor.execute(sql,(Next_checktime,check_detail['id']))
					connection.commit()
					logging.info('该监控阀值的当前时间:' + str(Next_checktime))
					#产生空告警报告
					curday = datetime.date.today()
					oldcurtime_str = datetime.datetime.strftime(check_detail['Next_checktime'], '%Y/%m/%d %H:%M:%s')
					curtime_str = datetime.datetime.strftime(Next_checktime, '%Y/%m/%d %H:%M:%s')
					m_logger = '警告：' +  oldcurtime_str + '至' + \
				curtime_str + '未收到任何告警,原计划应该收取' + str(N) + '条。' 
					sql = "INSERT INTO moniter_m_report (project_nick,host_nick,db_nick,m_date,m_timestamp,m_type,m_dim,m_value,m_status,m_send_status,description,timestamp_v)	VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					cursor.execute(sql, (check_detail['project_nick'],check_detail['host_nick'],check_detail['db_nick'],curday, None,check_detail['m_type'],check_detail['m_dim'],check_detail['m_value'],'error','未发送',m_logger,curtime ))
	#释放数据库连接	
	connection.close()	
	logging.info('监控时间校正结束，共校正监控阀值' + str(count) + '处')		






while True:
	curtime = datetime.datetime.now()		
	delta = datetime.timedelta(minutes=5)
	auto_update_Nexttime(curtime,delta)
	check_real_report(curtime,delta)
	logging.info('进入休眠')
	time.sleep(10)
