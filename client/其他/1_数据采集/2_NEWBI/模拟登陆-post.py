import requests

login_page  = 'http://10.4.33.156/login.html'
url = 'http://10.4.33.156/#/dashboard/home'
headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    }
data = {'name':'lining@bi.com', "password":'newbiroot,123'}

cookies = 'SESSION=8989db1a-19c9-4d0c-b4ea-690cf0a7c634'
res = requests.get(url, cookies = cookies, headers = headers)
#
# print res.status_code