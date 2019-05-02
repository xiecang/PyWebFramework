# -*- coding: utf-8 -*-
import socket
from urllib.parse import unquote

from routes import route_dict, route_static
from utils import log


class Request(object):
    """用于保存请求的数据"""

    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.headers = {}
        self.cookies = {}
        self.body = ''

    def add_cookies(self):
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        [
            'Accept-Language: zh-CN,zh;q=0.8'
            'Cookie: height=180; user=fc'
        ]
        """
        self.headers = {}
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # 清除 cookies
        self.cookies = {}
        self.add_cookies()

    def form(self):
        """
        form 函数用于把 body 解析为一个字典并返回
        body 的格式如下 a=b&c=d&e=1
        """
        args = self.body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[unquote(k)] = unquote(v)
        return f


request = Request()


def error(code: int = 404) -> bytes:
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def parsed_path(path: str) -> tuple:
    """解析请求路径和参数"""
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path: str) -> bytes:
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = {
        '/static': route_static,
    }
    r.update(route_dict)
    response = r.get(path, error)
    return response(request)


def received_request(connection: socket) -> bytes:
    buffer_size = 2000
    r = b''
    while True:
        req = connection.recv(buffer_size)
        r += req
        if len(req) < buffer_size:
            break
    return r


def run(host='', port=3000):
    """
    启动服务器
    """
    log(f"server start {host}:{port}")
    with socket.socket() as s:
        s.bind((host, port))
        while True:
            s.listen(5)
            connection, address = s.accept()
            r = received_request(connection)
            r = r.decode('utf-8')
            log(f"原始请求 {r}")
            if len(r.split()) < 2:
                continue

            path = r.split()[1]
            request.method = r.split()[0]
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            request.body = r.split('\r\n\r\n', 1)[1]
            header = r.split('\r\n\r\n', 1)[0]
            response = response_for_path(path)
            connection.sendall(response)
            connection.close()


if __name__ == '__main__':
    config = dict(
        host='127.0.0.1',
        port=3000,
    )
    run(**config)
