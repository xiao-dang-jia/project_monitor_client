from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from .models import m_d_real, m_report_detail
# Register your models here.
#在admin显示内容
class m_d_realAdmin(admin.ModelAdmin):
	list_display = [
		'project_nick',
		'server_ip',
		'm_type',
		'm_dim',
		'm_value',
		'm_logger',
		'm_timestamp'
	]
	list_filter = ('project_nick','server_ip',('m_timestamp',DateRangeFilter),)
#在admin显示组内容
class m_report_detailAdmin(admin.ModelAdmin):
	list_display = ['m_timestamp','project_nick','server_ip','m_type','m_dim','m_value',		'm_status','description','timestamp_v',
		]
	list__filter = ('project_nick','server_ip',('m_timestamp,DateRangeFilter'))







admin.site.register(m_d_real, m_d_realAdmin)
admin.site.register(m_report_detail, m_report_detailAdmin )
