#coding:utf-8
"""
成功
"""

import urllib2

url = 'http://10.4.33.156/login.html'

url2= 'http://10.4.33.156/#/dashboard/home'
## 直接将COOKIE 放入到HEADER中
headers={'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",'cookie': "SESSION=8989db1a-19c9-4d0c-b4ea-690cf0a7c634"}   #把cookie加进来

req = urllib2.Request(url2, headers=headers)

result = urllib2.urlopen(req)
print result.getcode()
