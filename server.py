import socket
import _thread

from request import Request
from utils import log

from models.base_model import SQLModel

from routes import error

from routes.routes_todo import route_dict as todo_routes
from routes.routes_weibo import route_dict as weibo_routes
from routes.routes_user import route_dict as user_routes
from routes.routes_public import route_dict as public_routes


def response_for_path(request):
    r = {}
    # 注册外部的路由
    r.update(todo_routes())
    r.update(weibo_routes())
    r.update(user_routes())
    r.update(public_routes())
    response = r.get(request.path, error)
    log('request', request, response)
    return response(request)


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            request = request.decode()
            log('request\n {}'.format(request))
            return request


def process_request(connection):
    with connection:
        r = request_from_connection(connection)
        log('request log:\n <{}>'.format(r))
        request = Request(r)
        response = response_for_path(request)
        log("response log:\n <{}>".format(response))
        connection.sendall(response)


def run(host, port):
    """
    启动服务器
    """
    # 初始化 ORM
    SQLModel.init_db()
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('ip {}'.format(address))
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='127.0.0.1',
        port=3000,
    )
    run(**config)
