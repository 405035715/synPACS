import urllib.request
import urllib.parse
import json


#提交报告
def submitReport():
    pass

# login
def login(name = '18072996469',password = '123456'):
    data = urllib.parse.urlencode({'username': name, 'password': password})
    data = data.encode('utf-8')
    with urllib.request.urlopen('http://121.40.19.7/api/doctor/login', data) as f:
        reponse = f.read().decode('utf-8')
        reponseDic = json.loads(reponse) #json转Dic
        print(reponseDic)
        print(reponseDic['user']['token'])




if __name__ == "__main__":
    print('test')
    login()
