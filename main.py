from requests.exceptions import ConnectionError, ReadTimeout, ChunkedEncodingError
from common.config import warning, Pool
from threadpool import ThreadPool
from threadpool import makeRequests
from threading import Lock
from requests import get
from time import sleep
from spider import *
from parse import *
lock = Lock()
p = Pool()


class IpPoolConfig:
    def __init__(self):
        f = open('domain.txt', 'r', encoding='utf-8')
        # 从domain.txt文件读取ip采集网站名字以及对应的函数名字
        self.dict_name = {}
        for item in f.read().split('\n'):
            if item:
                key, value = item.split('-')
                self.dict_name.update({key: value})
        f.close()
        # 检测代理的测试网站
        self.check_url = 'http://www.icanhazip.com/'
        # 采集代理的时间间隔
        self.wait_time = 5
        # 保存临时代理队列的大概容量
        self.size = 50

    def run_by_name(self, name):
        try:
            for item in eval(f'request_{self.dict_name[name]}')():
                iterator = eval(f'parse_{self.dict_name[name]}')(item)
                for i in iterator:
                    lock.acquire()
                    print(f'pick up {i}')
                    p.put('queue', i)
                    lock.release()
                # 将代理放入队列后 检查队列容量是否满足 若不满，则在此处等待；若满足，则继续采集
                while 1:
                    lock.acquire()
                    if p.info('queue') < self.size:
                        lock.release()
                        break
                    else:
                        lock.release()
                        sleep(2)
                sleep(2)
        except KeyError:
            warning(f'未找到<{name}>相关的spider或parse函数')
            print(f'未找到<{name}>相关的spider或parse函数')
            return None

    def check_valid(self, table_name):
        while 1:
            lock.acquire()
            if p.info(table_name) > 0:
                item = p.pop(table_name)
                lock.release()
                proxy = {'http': item}
                try:
                    response = get(url=self.check_url, proxies=proxy, timeout=self.wait_time)
                    if response.status_code == 200:
                        lock.acquire()
                        p.put('pool', item)
                        print(f'{item} valid.')
                        lock.release()
                    else:
                        print(f'{item} invalid.')
                except ConnectionError:
                    print(f'{item} invalid.')
                    pass
                except TimeoutError:
                    print(f'{item} invalid.')
                    pass
                except ReadTimeout:
                    print(f'{item} invalid.')
                    pass
                except ChunkedEncodingError:
                    print(f'{item} invalid.')
                    pass
            else:
                lock.release()
                sleep(1)


class IpPool(IpPoolConfig):
    def run(self, numb=20):
        thread = ThreadPool(numb)
        # 读取domain文件中的代理网站列表
        f = open('domain.txt', 'r', encoding='utf-8')
        name_list = [i[:i.index("-")] for i in f.read().split('\n') if i]
        f.close()
        # 必选：分配4线程用于测试queue队列的代理有效性1线程测试pool队列的代理有效性
        task1 = makeRequests(self.check_valid, ['queue'] * 4 + ['pool'])
        task2 = makeRequests(self.run_by_name, name_list)
        for task in task1:
            thread.putRequest(task)
        for task in task2:
            thread.putRequest(task)
        thread.wait()


if __name__ == '__main__':
    a = IpPool()
    a.run()
