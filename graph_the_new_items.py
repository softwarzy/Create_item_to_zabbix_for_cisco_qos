import requests
import json
import re
import pandas as pd

url = "http://192.166.5.14/api_jsonrpc.php"

#登录zabbix，返回token
def login_then_get_authkey(url):
    headers = {
        "Content-Type": "application/json-rpc"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params":
            {
                "user": "Admin",
                "password": "zabbix"
            },
        "id": 1
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    authkey = r.json()["result"]
    return authkey

#获取zabbix已有items，请在payload内定义关键字，返回清单：itemid/name
def get_qos_items(url,authkey):
    headers = {
        "Content-Type": "application/json-rpc"
    }
    payload = '{"jsonrpc":"2.0","method":"item.get","params":{"output":["itemid","name"],"hostid": "10254","search":{"name":"QOS G","hostid": "10254"},"sortfield":"itemid"},"auth":"'+ authkey + '","id":1}'
    r = requests.post(url, data=payload, headers=headers)
    content = r.json()["result"]
    return content

#post创建图表的请求，带json
def post_graph_create(url, payload):
    headers = {
        "Content-Type":"application/json-rpc"
    }
    r = requests.post(url, data=payload, headers=headers)
    return r.json()

#获取token
authkey = login_then_get_authkey(url)

#with open("qos graph 2.txt",'r') as f:
#    a = f.readlines()
#    f.close()
#content = ''.join(a)
#del a

#获取zabbix上已有的items
content = get_qos_items(url, authkey)

#将元组列表，转换成两个list
itemids = [ i["itemid"]  for i in  content]
names = [ i["name"].split()[1]  for i in  content]

#把上面的list转换成pandas的framedata格式
data = dict(itemids=itemids, names=names)
framdata = pd.DataFrame(data)
#将接口名称列表去重
intmembers = list(set(names))

print("It will create " + str(len(intmembers)) + " graphs!")
#定义颜色
colorlist = ["1A7C11", "F63100", "2774A4", "A54F10", "FC6EA3", "6C59DC", "AC8C14", "611F27", "F230E0", "5CCD18", "BB2A02", "5A2B57", "89ABF8", "7EC25C"]

#为每一个要生成的图表，定义jason，并post请求
for i in range(len(intmembers)):
    tmpframdata = framdata[framdata["names"] == intmembers[i]]["itemids"].tolist()
    payload = ''
    tmplist = list()
    print(intmembers[i])
    print(i)
    print(tmpframdata)
    for e in range(len(tmpframdata)):
        tmplist.append('"itemid":"' + str(tmpframdata[e]) + '","color":"' + str(colorlist[e]) + '"')
    payload = '},{'.join(tmplist)
    payload = '{"jsonrpc":"2.0","method":"graph.create","params":{"name":"QOS ' + str(intmembers[i]) + '","width":900,"height":300,"gitems":[{' + payload + '}]},"auth":"' + authkey + '","id":1}'
    result = post_graph_create(url, payload)
    if "result" in result:
        print("Create the" + str(i) + "graph QOS" + str(intmembers[i]))
    elif "error" in result:
        print(result["error"])
        print("some error happened when create graph QOS" + str(intmembers[i]))
    del tmpframdata,payload,tmplist,result
del authkey,content,itemids,names,data,framdata,intmembers,colorlist
