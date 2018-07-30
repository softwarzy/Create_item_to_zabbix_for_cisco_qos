import requests
import json
import pickle

with open("final.pkl",'rb') as f:
    finallist = pickle.load(f)
    f.close()

#运行之前,请输入url

url = "http://*.*.*.*/api_jsonrpc.php"

#登陆获得token
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

#向zabbix发post请求创建item
def post_item_create(url, payload):
    headers = {
        "Content-Type":"application/json-rpc"
    }
    r = requests.post(url, data=payload, headers=headers)
    return r.json()

#数据结构整形
def regular_the_payload(finallist):
    tmplist = finallist
    outputpayload = list()
    for i in range(len(tmplist)):
        outputpayload.append([])
        for e in range(len(tmplist[i])):
            for [cat, oid] in [["Dropped", "1.3.6.1.4.1.9.9.166.1.15.1.1.18"],["Transmitted", "1.3.6.1.4.1.9.9.166.1.15.1.1.11"]]:
                tmpstr=' "name": "QOS {ID4} {ID5} {ID6} {catogory}","snmp_community": "{SNMP_COMMUNITY}","snmp_oid": "{OID}.{ID0}.{ID1}","key_": "net.if.qos[{catogory}.{ID6}.{ID3}]","hostid": "10254","type": "4","interfaceid": "2","delay": "180","history": "30d","trends": "365d","value_type": "3","units": "bps","application":["1550"]'.format(ID0=finallist[i][e][0], ID1=finallist[i][e][1], ID3=finallist[i][e][3], ID4=finallist[i][e][4],ID5=finallist[i][e][5], ID6=finallist[i][e][6], catogory=cat, OID=oid, SNMP_COMMUNITY='{$SNMP_COMMUNITY}')
                outputpayload[i].append(tmpstr)
    return outputpayload

#进一步整形到json组成的list形式
def regulaer_whole_payload(jsonlist,authkey):
    tmp = jsonlist
    string1 = '{"jsonrpc":"2.0","method":"item.create","params":{'
    string2 = '},"auth":"'
    string3 = '","id":1}'
    output = list()
    for i in range(len(tmp)):
        output.append([])
        for e in range(len(tmp[i])):
            output[i].append(string1+tmp[i][e]+string2+authkey+string3)
    return output


#主程序
authkey = login_then_get_authkey(url)
print(authkey)
test = regular_the_payload(finallist)
item = regulaer_whole_payload(test, authkey)
#for-loop，完成post请求
for i in range(len(item)):
    for e in range(len(item[i])):
            result = post_item_create(url,item[i][e])
            if "result" in result:
                print("Create item{"+str(i)+"]["+str(e)+"]")
            elif "error" in result:
                print(item[i][e])
                print("some error happened at item["+str(i)+"]["+str(e)+"]")




