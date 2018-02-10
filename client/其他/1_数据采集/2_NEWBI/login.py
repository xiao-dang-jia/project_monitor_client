# coding:utf-8
import urllib2
import urllib
import cookielib
import re
import requests

login_page = "http://10.4.33.156/login.html"
headers = {
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        }
data = {"username": "lining@bi.com", "password": "liningbi"}

# 获得一个cookieJar实例
cj = cookielib.CookieJar()
# cookieJar作为参数，获得一个opener的实例
r = requests.post(login_page, cookies=cj, data=data)
print r.content

# html = renrenBrower("http://10.4.33.156/#/dashboard/home", 'lining@bi.com', 'liningbi')
# print html