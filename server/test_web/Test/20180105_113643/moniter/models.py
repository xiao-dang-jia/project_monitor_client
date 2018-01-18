from django.db import models

# Create your models here.
#存储客户端发过来监控数据
class m_d_real(models.Model):
	project_nick = models.CharField("监控项目",max_length=255, null=True)
	server_ip = models.GenericIPAddressField("服务器IP",max_length=255, null=True)
	m_type = models.CharField("监控类型",max_length=255, null=True)
	m_dim = models.CharField("监控维度",max_length=255, null=True)
	m_value = models.CharField("监控值",max_length=255, null=True)
	m_logger = models.TextField("监控日志", null=True)
	m_timestamp = models.DateTimeField("客户端时间戳", null=True)
	def __unicode__(self):
		return self.server_ip
	class Meta:
		verbose_name_plural = "监控数据详情(m_d_real)"
		verbose_name = "数据条目"
		
#存储服务端生成的report报告数据
class m_report_detail(models.Model):
	project_nick = models.CharField("监控项目",max_length=250, null=True)
	server_ip = models.GenericIPAddressField("服务器IP",max_length=255, null=True)
	#m_date = models.DateTimeField("服务端时间戳",null=True)
	m_timestamp = models.DateTimeField("客户端时间戳", null=True)
	m_type = models.CharField("监控类型",max_length=255, null=True)
	m_dim = models.CharField("监控维度",max_length=255, null=True)
	m_value = models.CharField("监控值",max_length=255, null=True)
	m_status = models.CharField("监控状态",max_length=255, null=True)
	m_send_status = models.CharField("发送状态",max_length=255, null=True)
	description = models.TextField("详细描述",max_length=255, null=True)
	timestamp_v = models.CharField("?",max_length=255, null=True)
	class Meta:
		verbose_name_plural = "监控报告(m_report_detail)"
		verbose_name = "数据条目"

	
 

