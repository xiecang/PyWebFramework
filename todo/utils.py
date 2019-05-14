# -*- coding: utf-8 -*-
import os
import time

from jinja2 import FileSystemLoader, Environment


def log(*args, **kwargs):
    format_ = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format_, value)
    print(dt, *args, **kwargs)


path = '{}/templates/'.format(os.path.dirname(__file__))
loader = FileSystemLoader(path)
env = Environment(loader=loader)


def template(path: str, **kwargs):
    """
    本函数接受一个路径和一系列参数
    读取模板并渲染返回
    """
    t = env.get_template(path)
    return t.render(**kwargs)


def response_with_headers(headers: dict, status_code=200):
    header = 'HTTP/1.1 {} OK\r\n'.format(status_code)
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header


def redirect(location: str, headers: dict = None):
    h = {
        'Content-Type': 'text/html',
    }
    if headers is not None:
        h.update(headers)
    h['Location'] = location
    # 302 状态码的含义, Location 的作用
    header = response_with_headers(h, 302)
    r = header + '\r\n' + ''
    return r.encode(encoding='utf-8')


def http_response(body: str, headers: dict = None):
    """
    headers 是可选的字典格式的 HTTP 头
    """
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    if headers is not None:
        header += ''.join(['{}: {}\r\n'.format(k, v)
                           for k, v in headers.items()])
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')
