from django.conf.urls import url, include
from . import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = [
#	url(r'^$', include(admin.site.urls), name = 'index'),
	url(r'^api/collect$', views.collect),
	url(r'^api/gethost/.json$', views.gethosts)
	
]
