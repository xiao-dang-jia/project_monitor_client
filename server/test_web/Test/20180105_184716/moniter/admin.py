from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from .models import m_d_real,m_report
# Register your models here.
#在admin显示内容
class m_d_realAdmin(admin.ModelAdmin):
	list_display = [
		'project_nick',
		'host_nick',
		'db_nick',
		'm_type',
		'm_dim',
		'm_value',
		'm_logger',
		'm_timestamp',
		'timestamp_v',
	]
	list_filter = ('project_nick','host_nick',('m_timestamp',DateRangeFilter),)
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			self.readonly_fields = []
		return self.readonly_fields
	readonly_fields = [
		'project_nick',
		'host_nick',
		'db_nick',
		'm_type',
		'm_dim',
		'm_value',
		'm_logger',
		'm_timestamp',
		'timestamp_v',
	]
class m_reportAdmin(admin.ModelAdmin):
	list_display = [
		'project_nick',
		'host_nick',
		'db_nick',
		'm_date',
		'm_type',
		'm_dim',
		'm_value',
		'm_status',
		'm_send_status',
		'description',
		'm_timestamp',
		'timestamp_v',
	]
	list_filter = ('project_nick','host_nick',('m_timestamp',DateRangeFilter),)
	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			self.readonly_fields = []
		return self.readonly_fields
	readonly_fields  = [
		'project_nick',
		'host_nick',
		'db_nick',
		'm_date',
		'm_type',
		'm_dim',
		'm_value',
		'm_status',
		'm_send_status',
		'description',
		'm_timestamp',
		'timestamp_v',
	]





admin.site.register(m_d_real, m_d_realAdmin)
admin.site.register(m_report, m_reportAdmin)
