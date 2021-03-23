import json
import time
import sys
import requests
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

parser = argparse.ArgumentParser()
parser.add_argument("-r", help = "URL 列表文件") # url列表名字
parser.add_argument("-m", help = "最大扫描数") # 最大扫描数
parser.add_argument("-t", help = "超过最大扫描数时的等待时间") # 超过最大扫描数时的等待时间
args = parser.parse_args()

requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # 关闭提示

def get_scans_num(url, headers):

    '''
    获取当前正在扫描的目标数
    scans_running_count 正在扫描的个数
    scans_conducted_count 扫完的个数
    targets_count 总个数
    '''

    r = requests.get(url=url, headers=headers, verify=False).text
    my_dict = json.loads(r)
    return int(my_dict['scans_running_count'])


def get_target(target_file): 
    '''
    从本地获取url
    '''
    try:
        with open(target_file, "r", encoding='utf-8') as f:
            content = f.read().splitlines()
        return content
    except Exception as e:
        print("\n未找到文件！\n")
        sys.exit(0)


def add_targets(url_list, headers, total_target_url):
    '''
    添加目标，已有的不添加
    '''
    count = 1

    r = requests.get(url = total_target_url, headers = headers, verify = False).text
    my_dict = json.loads(r)

    for i in my_dict['targets']:
        if str(i['address']) in url_list: # 获取已有目标
            url_list.remove(str(i['address']))

    if len(url_list) == 0:
        print('\n目标已全部添加！\n')
    
    else:
        zican_name = input('输入资产名字：\n')
        for i in url_list:
            data = {
                "address" : str(i),
                "description" : zican_name,
                "criticality" : "20"
            }
            r = requests.post(url = total_target_url, headers = headers, verify = False, data = json.dumps(data))

            #my_dict = json.loads(r)
            #target_id.append(str(my_dict['target_id'])) # 返回已添加的target id
            count += 1

        print('\n本次添加了' + str(count-1) + '个目标\n')


def add_scans(add_scan_url, headers, total_target_url, count):
    count = count
    target_id = []
    #sys.exit(0)

    r = requests.get(url = total_target_url, headers = headers, verify = False).text
    my_dict = json.loads(r)
    #print(my_dict)
    
    for i in my_dict['targets']:
        if i['last_scan_session_status'] == None: # 没扫过的就添加扫描
            target_id.append(i['target_id'])

    for i in target_id: # 速度设置
        url = 'https://127.0.0.1:3443/api/v1/targets/' + str(i) + '/configuration'
        data = {
                "scan_speed":"moderate"
            }
        r = requests.patch(url = url, data = json.dumps(data), headers = headers, verify = False)
        scans_num = get_scans_num(dashbord_url, headers) # 获取当前扫描数
        
        if int(scans_num) >= int(args.m):
            print('\n当前扫描数已超过最大设定值，等待' + str(args.t) + '秒后再次扫描。\n')
            time.sleep(int(args.t))
            add_scans(add_scan_url, headers, total_target_url, count)

        elif int(scans_num) < int(args.m):
            data = {
                        "target_id": str(i),
                        "profile_id": "11111111-1111-1111-1111-111111111111",
                        "schedule": {
                                        "disable":False,
                                        "start_date":None,
                                        "time_sensitive":False
                                }
                }
            r = requests.post(url = add_scan_url, data = json.dumps(data), headers = headers, verify = False).text
            count += 1
            print('添加第' + str(count) + '个目标扫描。\n')
            time.sleep(1)
            if count % int(args.m) == 0:
                print('检查扫描数中，等待十秒。。\n')
                time.sleep(10)
            

def main():
    count = 0
    target_list = get_target(args.r) # 获取url列表
    add_targets(target_list, headers, total_target_url) # 添加目标
    add_scans(add_scan_url, headers, total_target_url, count)    



if __name__ == '__main__':
    api_key = '1986ad8c0a5b3df4d7028d5f3c06e936ce89601c61a9244cebd708814019c8adf' # apikey
    total_target_url = 'https://127.0.0.1:3443/api/v1/targets' # 获取所有目标信息
    dashbord_url = 'https://127.0.0.1:3443/api/v1/me/stats' # 基本信息面板
    add_scan_url = 'https://127.0.0.1:3443/api/v1/scans' # 添加扫描url
    headers = {
        'X-Auth': api_key,
        'Content-type': 'application/json'
    }
    main()

