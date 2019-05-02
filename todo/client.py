# -*- coding: utf-8 -*-
import socket
import ssl

from utils import log


def parsed_url(url: str) -> tuple:
    """
    解析 url 返回 (protocol host port path)
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        # '://' 定位 然后取第一个 / 的位置来切片
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    # 默认端口
    port = port_dict[protocol]
    if ':' in host:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocol(protocol: str) -> socket:
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s: socket) -> bytes:
    """返回这个 socket 读取的所有数据"""
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(response: str) -> tuple:
    """
    把 response 解析出 状态码 headers body 返回
    状态码是 int
    headers 是 dict
    body 是 str
    """
    header, body = response.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    code = h[0].split()[1]
    status_code = int(code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


def path_with_query(path: str, query: dict) -> str:
    """返回一个拼接后的 url"""
    q =''
    for k, v in query.items():
        q = path + '?' + str(k) + '=' + str(v) + '&' + q
    return q[:-1]


def get(url: str, query: dict = None) -> tuple:
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)
    if query is not None:
        path = path_with_query(path, query)
    s = socket_by_protocol(protocol)
    s.connect((host, port))

    request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = response_by_socket(s)
    log('get response: \n', str(response))
    r = response.decode(encoding)

    status_code, headers, body = parsed_response(r)
    if status_code in [301, 302]:
        url = headers['Location']
        return get(url)

    return status_code, headers, body


def main():
    url = 'http://movie.douban.com/top250'
    status_code, headers, body = get(url)
    print('main', status_code)
    print('main headers ({})'.format(headers))
    print('main body', body)


if __name__ == '__main__':
    main()
