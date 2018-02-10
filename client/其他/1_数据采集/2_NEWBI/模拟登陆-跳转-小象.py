#coding:utf-8

import urllib2
import urllib
import cookielib


login_url = 'http://10.4.33.156/login.html'

view_url = 'http://10.4.33.156/#/dashboard/home'
## 直接将COOKIE 放入到HEADER中
headers={'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}   #把cookie加进来

if __name__ == '__main__':
    data = {'name':'lining@bi.com', "password":'newbiroot,123'}
    payload = urllib.urlencode(data)

    # use cookiejar
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    request = urllib2.Request(login_url, payload , headers=headers)
    response = urllib2.urlopen(request)
    for cookie in cj:
        print cookie.name, cookie.value, cookie.domain
    print response.info()
