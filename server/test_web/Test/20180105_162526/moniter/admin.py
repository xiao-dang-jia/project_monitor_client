from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from .models import m_d_real
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






admin.site.register(m_d_real, m_d_realAdmin)
