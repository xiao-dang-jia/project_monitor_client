import requests
import request

url = 'http://10.4.33.156/login.html'

headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    }

data = {'name':'lining@bi.com', "password":'newbiroot,123'}

reponse = requests.get(url,params=data)
print(reponse.url)