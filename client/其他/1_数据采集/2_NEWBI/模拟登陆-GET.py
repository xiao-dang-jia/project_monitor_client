import requests

login_page  = 'http://10.4.33.156/login.html'
url = 'http://10.4.33.156/#/dashboard/home'
headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    }
data = {'name':'lining@bi.com', "password":'newbiroot,123'}

res = requests.post(login_page, data = data, headers = headers)

print res.status_code
# res1 = requests.get(url, cookies = res.cookies, headers = headers)
#
# print res1.content