from routes import (
    current_user,
    html_response,
    redirect
)
from utils import log


def index(request):
    """
    首页的路由函数
    """
    u = current_user(request)
    return html_response('index.html', username=u.username)


def static(request):
    """
    静态资源的路由函数
    """
    filename = request.query.get('file')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.x 200 OK\r\nContent-Type: image/gif\r\n\r\n'
        img = header + f.read()
        return img


def route_dict():
    d = {
        '/': index,
        '/static': static,
    }
    return d
