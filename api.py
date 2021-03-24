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
            content = list(set(content))
        return content
    except Exception as e:
        print("\n未找到文件！\n")
        sys.exit(0)


def add_targets(url_list, headers, total_target_url):
    '''
    添加目标
    '''
    count = 1
    target_id = []

    r = requests.get(url = total_target_url, headers = headers, verify = False).text
    
    zican_name = input('输入资产名字：\n')
    for i in url_list:
        data = {
            "address" : str(i),
            "description" : zican_name,
            "criticality" : "20"
        }
        r = requests.post(url = total_target_url, headers = headers, verify = False, data = json.dumps(data)).text
        my_dict = json.loads(r)
        target_id.append(my_dict["target_id"])
        count += 1

    print('\n本次添加了' + str(count-1) + '个目标\n')
    return target_id


def add_scans(add_scan_url, headers, total_target_url, count, target_id):
    '''
    添加扫描目标
    '''
    count = count
    for i in target_id: # 速度设置
        url = 'https://127.0.0.1:3443/api/v1/targets/' + str(i) + '/configuration'
        data = {
                "scan_speed":"moderate"
            }
        r = requests.patch(url = url, data = json.dumps(data), headers = headers, verify = False)
        scans_num = get_scans_num(dashbord_url, headers) # 获取当前扫描数
        
        while int(scans_num) >= int(args.m):
            print('\n当前扫描数已超过最大设定值，等待' + str(args.t) + '秒后再次扫描。\n')
            time.sleep(int(args.t))
            scans_num = get_scans_num(dashbord_url, headers)
       
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
    print('\n添加结束！\n')
            

def main():
    count = 0
    target_list = get_target(args.r) # 获取url列表
    target_id = add_targets(target_list, headers, total_target_url)
    add_scans(add_scan_url, headers, total_target_url, count, target_id)


if __name__ == '__main__':
    api_key = 'xxxxxxxxxx' # apikey
    total_target_url = 'https://127.0.0.1:3443/api/v1/targets' # 获取所有目标信息
    dashbord_url = 'https://127.0.0.1:3443/api/v1/me/stats' # 基本信息面板
    add_scan_url = 'https://127.0.0.1:3443/api/v1/scans' # 添加扫描url
    headers = {
        'X-Auth': api_key,
        'Content-type': 'application/json'
    }
    main()
