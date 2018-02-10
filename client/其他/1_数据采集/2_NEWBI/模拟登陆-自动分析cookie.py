#encoding=utf-8
import urllib2
import urllib
import cookielib
import re

def renrenBrower(url,user,password):

    login_page = "http://10.4.33.156/login.html"   #抓包分析post地址
    try:
        #构造一个opener来贮存cookie,每次都用opener来请求就可以.
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0')]
        data = urllib.urlencode({"email":user,"password":password})
        opener.open(login_page,data)  #先请求post的url地址，拿到cookie之后再请求需要登录后才能访问的url，就是下一行。
        op=opener.open(url)   #利用得到的cookie请求该页面
        data = op.read()
        return data
    except Exception,e:
         print str(e)

html = renrenBrower("http://10.4.33.156/#/dashboard/home",'lining@bi.com','liningbi')  #帐号和密码自己填
print html
