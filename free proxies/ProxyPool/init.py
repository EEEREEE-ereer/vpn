import time
import proxy_pool

if __name__ == '__main__':
    num = 0
    proxy_pool = proxy_pool.proxyPool()
    test_url = 'https://www.baidu.com'
    while True:
        now=time.localtime()

        start_time = time.time()
        current_num=proxy_pool.get_count()
        ip_list = proxy_pool.GetFreeProxyList()
        good_ip_list = proxy_pool.Check_ippool(ip_list=ip_list, test_url=test_url, threading_num=20)
        end_time = time.time()
        d_time = end_time - start_time

        print("第 " + str(num) + " 次" + "运行时间为：%.6s 秒" % d_time)
        print('当前数据库内可用数：%i' % proxy_pool.get_count()+'|| 本次新加代理数：%i'%(proxy_pool.get_count()-current_num))
        num = num + 1
        if now.tm_hour>9 and now.tm_hour<22:
            print('当前为工作时间：休息%i秒'%60)
            time.sleep(60)
        else:
            print('当前为夜晚休息时间：休息%i秒'%600)
            time.sleep(600)
