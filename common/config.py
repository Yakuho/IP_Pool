from logging import basicConfig, WARNING, error, warning
from unittest import TestCase
from requests.exceptions import MissingSchema
from requests import request
from redis import Redis


class LoggingSetting(TestCase):
    format_info = '[%(asctime)s %(filename)s-%(levelname)s]: %(message)s'
    basicConfig(filename='./log/错误日志.log', format=format_info, level=WARNING, filemode='a',
                datefmt='%Y-%m-%d-%I:%M:%S %p')


class Pool:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = Redis(host=host, port=port, db=db, decode_responses=True)

    def pop(self, table_name):
        return self.redis.spop(table_name)

    def put(self, table_name, data):
        self.redis.sadd(table_name, data)

    def drop(self, table_name):
        self.redis.delete(table_name)

    def info(self, table_name):
        return int(self.redis.scard(table_name))


def request_(url, method, **kwargs):
    try:
        response = request(url=url, method=method, **kwargs)
        if response.status_code == 200 or response.status_code == 302:
            return response.text
        else:
            warning(f'URL: {url} 状态码为:{response.status_code}')
            return -1
    except TimeoutError:
        print(f'访问 {url} 超时')
        error(f'访问 {url} 超时')
        return -1
    except MissingSchema:
        print(f'URL: {url} 无效')
        error(f'URL: {url} 无效')
        return -2
    except:
        print(f'URL: {url} 出现未知错误')
        error(f'URL: {url} 出现未知错误')
        return -2


def requests(url, method, **kwargs):
    # 异常则重请求，直到重请求3次失败，则放弃
    # 超时等待时间线性增长 3 6 9 12
    for i in range(3):
        if 'timeout' not in kwargs: kwargs['timeout'] = 3 + i*3
        response = request_(url, method, **kwargs)
        if type(response) is str:
            return response
        elif response == -1:
            warning(f'URL: {url} 准备第{i+1}次重请求')
            continue
        else:
            return None
    else:
        warning(f'URL: {url} 3次重请求失败')
        return None
