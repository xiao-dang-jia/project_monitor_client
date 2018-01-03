import urllib
import urllib2

url = 'http://10.4.33.156/login.html'

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
    'cache-control': "no-cache",
    'connection': "keep-alive",
    'cookie': "SESSION=8989db1a-19c9-4d0c-b4ea-690cf0a7c634",
    'host': "10.4.33.156",
    'if-modified-since': "Fri, 28 Jul 2017 06:43:28 GMT",
    'if-none-match': "\"597add10-31f0\"",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    }

data = {'name':'lining@bi.com', "password":'newbiroot,123'}

payload = urllib.urlencode(data)
request = urllib2.Request(url, payload , headers=headers)
response = urllib2.urlopen(request)