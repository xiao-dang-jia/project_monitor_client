from django.db import models

# Create your models here.

####存储监控数据与设置信息####
#*************************************************************************************
#存储监控项目阀值指标设置信息
class m_project_checklist(models.Model):
	send_id = models.IntegerField("发送IP",null=True)
	project_nick = models.CharField("项目别名",max_length=255, null=True)
	host_nick = models.CharField("主机别名",max_length=255, null=True)
	db_nick = models.CharField("数据库别名",max_length=255, null=True)
	m_type = models.CharField("监控类型",max_length=255, null=True)
	m_dim = models.CharField("监控维度",max_length=255, null=True)
	m_value_type = models.CharField("监控指标类型",max_length=255, null=True)
	m_value = models.CharField("监控指标",max_length=255, null=True)
	m_status = models.CharField("监控状态",max_length=255, null=True)
	m_interval_type = models.CharField("计划任务类型",max_length=255, null=True)
	m_interval_time = models.CharField("计划任务时间值",max_length=255, null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)

#存储客户端发过来监控数据
class m_d_real(models.Model):
	project_nick = models.CharField("项目别名",max_length=255, null=True)
	host_nick = models.CharField("主机别名",max_length=255, null=True)
	db_nick = models.CharField("数据库别名",max_length=255, null=True)
	m_type = models.CharField("监控类型",max_length=255, null=True)
	m_dim = models.CharField("监控维度",max_length=255, null=True)
	m_value = models.CharField("监控指标",max_length=255, null=True)
	m_logger = models.TextField("监控日志", null=True)
	m_timestamp = models.DateTimeField("客户端时间戳", null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)
	def __unicode__(self):
		return self.server_ip
	class Meta:
		verbose_name_plural = "监控数据详情(m_d_real)"
		verbose_name = "数据条目"
		
#存储服务端生成的report简要数据
class m_report(models.Model):
	project_nick = models.CharField("项目别名",max_length=250, null=True)
	host_nick = models.CharField("主机别名",max_length=255, null=True)
	db_nick = models.CharField("数据库别名",max_length=255, null=True)
	m_date = models.DateField("监控日期",null=True)
	m_timestamp = models.DateTimeField("监控时间", null=True)
	m_type = models.CharField("监控类型",max_length=255, null=True)
	m_dim = models.CharField("监控维度",max_length=255, null=True)
	m_value = models.CharField("监控值",max_length=255, null=True)
	m_status = models.CharField("监控状态",max_length=255, null=True)
	m_send_status = models.CharField("发送状态",max_length=255, null=True)
	description = models.TextField("详细描述",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)
	class Meta:
		verbose_name_plural = "监控报告(m_report)"
		verbose_name = "数据条目"

#存储服务端生成的report详细数据
class m_report_detail(models.Model):
	report_id = models.IntegerField("发送报告IP",null=True)
	rule_id = models.IntegerField("规则ID",null=True)
	logger = models.TextField("详细日志",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)
#存储发送告警的数据
class m_report_send(models.Model):
	report_id = models.IntegerField("发送报告IP",null=True)
	send_id = models.IntegerField("发送IP",null=True)
	send_type = models.CharField("发送类型",max_length=255, null=True)
	send_user = models.CharField("监控发送人",max_length=255, null=True)
	send_subject = models.CharField("监控主题",max_length=255, null=True)
	send_message = models.TextField("发送信息",null=True)
	is_send = models.CharField("是否发送",max_length=255, null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)
#存储发送告警设置信息
class m_rule_send(models.Model):
	type = models.CharField("是否发送",max_length=255, null=True)
	user = models.CharField("监控接收人",max_length=255, null=True)
	subject = models.CharField("主题",max_length=255, null=True)
	message =  models.TextField("详细描述",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)

#************************************************************************************
####存储项目、主机、数据库及用户信息####
#/////////////////////////////////////////////////////////////////////////////////////
#存储项目信息
class m_d_project(models.Model):
	nick = models.CharField("项目别名",max_length=255, null=True)
	name = models.CharField("项目名称",max_length=255, null=True)
	status = models.CharField("项目当前状态",max_length=255, null=True)
	content = models.TextField("详细描述",null=True)
	phase = models.CharField("项目期数",max_length=255, null=True)
	resource_id = models.CharField("资源情况",max_length=255, null=True)
	start_time = models.DateTimeField("开始时间", null=True)
	end_time = models.DateTimeField("结束时间", null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)
#存储主机信息
class m_d_host(models.Model):
	project_nick = models.CharField("项目别名",max_length=250, null=True)
	host_nick = models.CharField("主机别名",max_length=255, null=True)
	host = models.GenericIPAddressField("主机IP, null=True")
	port = models.CharField("主机端口号",max_length=255, null=True)
	description = models.TextField("详细描述",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)

#存储用户信息
class m_d_user(models.Model):
	type = models.CharField("用户类型",max_length=250, null=True)
	username = models.CharField("用户名",max_length=250, null=True)
	password = models.CharField("密码",max_length=250, null=True)
	description = models.TextField("详细描述",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)

#存储数据库信息
class m_d_db(models.Model):
	project_nick = models.CharField("项目别名",max_length=250, null=True)
	db_nick = models.CharField("数据库别名",max_length=250, null=True)
	db_type = models.CharField("数据库类型",max_length=250, null=True)
	host = models.GenericIPAddressField("主机IP, null=True")
	port = models.CharField("主机端口号",max_length=255, null=True)
	db_name = models.CharField("数据库名",max_length=255, null=True)
	schema_name = models.CharField("schema号",max_length=255, null=True)
	description = models.TextField("详细描述",null=True)
	timestamp_v = models.DateTimeField("入库时间", null=True)







#///////////////////////////////////////////////////////////////////////////////////// 

