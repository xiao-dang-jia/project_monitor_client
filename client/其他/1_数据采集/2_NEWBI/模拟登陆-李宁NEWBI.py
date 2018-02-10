# coding:utf-8
import urllib2
import urllib
import cookielib
import re


def renrenBrower(url, user, password):
    # 登陆页面，可以通过抓包工具分析获得，如fiddler，wireshark
    login_page = "http://10.4.33.156/login.html"
    try:
        # 获得一个cookieJar实例
        cj = cookielib.CookieJar()
        # cookieJar作为参数，获得一个opener的实例
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        headers = {
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        }
        # 伪装成一个正常的浏览器，避免有些web服务器拒绝访问。此处伪装的火狐
        opener.addheaders = [('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36')]
        # 生成Post数据，含有登陆用户名密码。
        data = urllib.urlencode({"email": user, "password": password})

        # request = urllib2.Request(login_page, data, headers= headers)
        # response = urllib2.urlopen(request)
        # print response
        # print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        # 以post的方法访问登陆页面，访问之后cookieJar会自定保存cookie
        opener.open(login_page, data)
        # 以带cookie的方式访问页面
        op = opener.open(url)
        # 读取页面源码
        data = op.read()
        return data

    # 异常处理
    except Exception, e:
        print str(e)
        # 访问某用户的个人主页，其实这已经实现了人人网的签到功能。


html = renrenBrower("http://10.4.33.156/#/dashboard/home", 'lining@bi.com', 'liningbi')
print html