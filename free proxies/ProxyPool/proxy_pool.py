# 感觉获取代理用不了多少时间，就采用单线程吧

import requests
from lxml import etree
from urllib import parse
import time
import threading
import pymongo

requests.timeout=20

# 就不传数据了，数据在各个子函数内定义
class proxyPool(object):
    def GetFreeProxyList(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }

        # 各个代理网站

        # 合并了四个代理网站
        def kuai_yun_qinghua_superfast():

            url_kuai='https://www.kuaidaili.com/free/inha/{num}'
            url_yun='http://www.ip3366.net/free/?stype=1&page={num}'
            url_qinghua='http://www.qinghuadaili.com/free/{num}/'
            url_superfast='http://www.superfastip.com/welcome/freeip/{num}'

            ip_list=[]
            for j in range(4):
                if j==0:
                    url=url_kuai
                elif j==1:
                    url=url_yun
                elif j==2:
                    url=url_qinghua
                elif j==3:
                    url = url_superfast
                for i in range(8):
                    temp_ip_list=[]
                    url=url.format(num=str(i+1))
                    try:
                        res=requests.get(url=url,headers=headers)
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError,
                            requests.exceptions.ConnectionError) :
                        continue
                    html=etree.HTML(res.content)
                    ip=html.xpath("//tr/td[1]")
                    port=html.xpath("//tr/td[2]")
                    temp_ip_list.extend(list(map(lambda ip, port: (ip.text + ':' + port.text), ip, port)))
                    if len(temp_ip_list):
                        ip_list[len(ip_list):len(ip_list)+len(temp_ip_list)-1]=temp_ip_list
                    # 重置url
                    if j == 0:
                        url = url_kuai
                    elif j == 1:
                        url = url_yun
                    elif j == 2:
                        url = url_qinghua
                    elif j == 3:
                        url = url_superfast

            return ip_list

        def _89():
            data = {
                "num": "100",
                "port": "",
                "address": "",
                "isp": ""
            }
            url = "http://www.89ip.cn/tqdl.html?api=1&" + str(parse.urlencode(data))
            try:
                res = requests.get(url=url, headers=headers)
                html = etree.HTML(res.content.decode(encoding='utf-8'))
                ip_list = html.xpath("//body/text()")[2:-1]
                ip_list[0] = ip_list[0].strip()
            except (requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError,
                            requests.exceptions.ConnectionError) as e:
                print(e)
                exit()
            return ip_list

        # 合并了两个
        def xila_nima():
            url_xila='http://www.xiladaili.com/gaoni/{num}'
            url_nima='http://www.nimadaili.com/gaoni/{num}'

            ip_list=[]
            for j in range(2):
                if j == 0:
                    url = url_xila
                elif j == 1:
                    url = url_nima
                for i in range(8):
                    url = url.format(num=str(i+1))
                    try:
                        res = requests.get(url=url, headers=headers)
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError,
                            requests.exceptions.ConnectionError) as e:
                        print(e)
                        continue
                    html = etree.HTML(res.content)
                    temp_ip_list=html.xpath("//tr//td[1]/text()")
                    if len(temp_ip_list):
                        ip_list[len(ip_list):len(ip_list)+len(temp_ip_list)-1]=temp_ip_list
                    # 重置url
                    if j == 0:
                        url = url_xila
                    elif j == 1:
                        url = url_nima
            return ip_list

        # 将各个子模块的数据传给ip_list
        ip_list=kuai_yun_qinghua_superfast()
        temp_ip_list=_89()
        ip_list[len(ip_list):len(temp_ip_list)+len(ip_list)-1]=temp_ip_list
        temp_ip_list = xila_nima()
        ip_list[len(ip_list):len(temp_ip_list) + len(ip_list) - 1] = temp_ip_list
        # 去除重复元素
        ip_list = list(set(ip_list))
        print('数据抓取完毕！本次需检查%i'%len(ip_list))
        return ip_list


    def Check_ippool(self, ip_list,
                     test_url='https://www.baidu.com', threading_num=10):
        # 多线程要用到的一些全局变量初始化
        global ip_list_new, index, success, fail, gLock, done
        ip_list_new = []
        index = -1
        success = 0
        fail = 0
        gLock = threading.Lock()
        done = 0

        # 加入数据库内已有代理
        db_ip_list = self.get_iplist(self.get_count())
        ip_list[len(ip_list):len(ip_list) + len(db_ip_list) - 1] = db_ip_list
        # 去除重复元素
        ip_list = list(set(ip_list))

        def Muti_Check_ip(ip_list, test_url):
            # 多线程检查ip

            global ip_list_new, index, success, fail, gLock, done
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36'
            }
            url = test_url
            total = len(ip_list)
            while True:
                gLock.acquire()
                if total > index + 1:
                    index = index + 1
                    ip = ip_list[index]
                    gLock.release()
                    proxies = {
                        'http': 'http://' + ip,
                        'https': 'https://' + ip
                    }
                    try:
                        res = requests.get(url=url, headers=headers, timeout=15, proxies=proxies, allow_redirects=False)
                        if res.status_code == 200:
                            ip_list_new.append(ip)
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ChunkedEncodingError,
                            requests.exceptions.ConnectionError) :
                        continue

                else:
                    done = done + 1
                    gLock.release()
                    break

        for x in range(threading_num):
            # 创建线程
            t = threading.Thread(target=Muti_Check_ip, args=([ip_list, test_url, ]))
            # 启动线程
            t.start()

        while True:
            if done == threading_num:
                # 清空已有数据，同时存入新数据
                self.delete()
                self.insert(ip_list_new)
                return ip_list_new
            else:
                time.sleep(5)
# 使用MongoDB存储代理
    # 初始化
    def __init__(self,host='127.0.0.1',port=27017):
        # 连接MongoDB
        self.client=pymongo.MongoClient(host=host,port=port)
        # 指定数据库
        self.db=self.client['ProxyPool']
        # 指定集合
        self.proxy=self.db['proxy']
        # 初始化索引
        self.proxy.ensure_index('ip',unique=True)

    # 插入
    def insert(self,ip_list):
        try:
            list=[]
            current_time=time.time()
            for item in ip_list:
                a={'ip':item,'add_time':current_time}
                list.append(a)
            self.proxy.insert(list)
        except Exception as e:
            print(e)

    # 删除
    def delete(self,conditions=None):
        try:
            self.proxy.remove(conditions)
        except Exception as e:
            print(e)

    # 获取
    def get(self,count,conditions=None):
        try:
            raw_data=self.proxy.find(conditions,limit=count)
            return raw_data
        except Exception as e:
            print(e)
        pass

    # 获取当前数据库内的代理数量
    def get_count(self):
        return self.proxy.count()

# 设置调用接口
    def get_oneip(self):
        proxy=self.get(1)
        return proxy[0]['ip']

    def get_iplist(self,num):
        current_num=self.get_count()
        if current_num<num:
            num=current_num
        ip_list=[]
        proxies=self.get(num)
        for item in proxies:
            ip_list.append(item['ip'])
        return ip_list
