from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import  m_d_real, m_report_detail
import json
# Create your views here.
#接收用户发过来的请求
def collect(request):
        req = request
        if req.POST:
                project_nick = req.POST.get('project_nick')
                server_ip = req.POST.get('server_ip')
                m_type = req.POST.get('m_type')
                m_dim = req.POST.get('m_dim')
                m_value = req.POST.get('m_value')
                m_logger = req.POST.get('m_logger')
                m_timestamp = req.POST.get('m_timestamp')
                host = m_d_real()
                host.project_nick = project_nick
                host.server_ip = server_ip
                host.m_type = m_type
                host.m_dim = m_dim
                host.m_value = m_value
                host.m_logger = m_logger
                host.m_timestamp = m_timestamp
                host.save()
                return HttpResponse('OK')
        else:
                return HttpResponse('no post data')
#提供给特殊客户机的API
def gethosts(req):
	return HttpRespinse('OK')
