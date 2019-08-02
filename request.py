import urllib.parse
from utils import log


class Request(object):
    def __init__(self, raw_data):
        # 只 split 一次，body 中可能有换行
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.path = ""
        self.query = {}
        self.parse_path(path)
        log('Request: path 和 query', self.path, self.query)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])
        log('Request: headers 和 cookies', self.headers, self.cookies)

    def add_headers(self, header):
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            k, v = cookies.split('=')
            self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f

    def parse_path(self, path):
        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query
