host='39.105.161.170'


from Proxy_Pool import proxy_pool

if __name__ == '__main__':
    pool=proxy_pool.proxyPool()
    pool.__init__(host=host)
    print('当前代理池内的代理数：%i'%pool.get_count())
    print(pool.get_iplist(20))
