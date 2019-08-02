import os.path
from urllib.parse import quote
import uuid

from jinja2 import (
    Environment,
    FileSystemLoader,
)

from models.session import Session
from models.user import User
from utils import log


def initialized_environment():
    parent = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent, 'templates')
    loader = FileSystemLoader(path)
    e = Environment(loader=loader)
    return e


class Template:
    e = initialized_environment()

    @classmethod
    def render(cls, filename, *args, **kwargs):
        template = cls.e.get_template(filename)
        return template.render(*args, **kwargs)


def current_user(request):
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        s = Session.one(session_id=session_id)
        if s is None or s.expired():
            return User.guest()
        else:
            user_id = s.user_id
            u = User.one(id=user_id)
            if u is None:
                return User.guest()
            else:
                return u
    else:
        return User.guest()


def error(request, code=404):
    e = {
        401: b'HTTP/1.x 404 Unauthorized\r\n\r\n<h1>Unauthorized</h1>',
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def formatted_header(headers, code=200):
    header = 'HTTP/1.1 {} OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url, session_id=None):
    h = {
        'Location': url,
    }
    if isinstance(session_id, str):
        h.update({
            'Set-Cookie': 'session_id={}; path=/'.format(session_id)
        })

    response = formatted_header(h, 302) + '\r\n'
    return response.encode()


def html_response(filename, **kwargs):
    body = Template.render(filename, **kwargs)
    headers = {
        'Content-Type': 'text/html',
    }
    header = formatted_header(headers)
    r = header + '\r\n' + body
    return r.encode()


def login_required(route_function):
    def f(request):
        log('login_required')
        u = current_user(request)
        if u.is_guest():
            log('游客用户')
            return redirect('/user/login/view')
        else:
            log('登录用户', route_function)
            return route_function(request)

    return f


csrf_tokens = dict()


def csrf_required(route_function):
    def f(request):
        log('csrf_required')
        token = request.query['token']
        u = current_user(request)
        if token in csrf_tokens and csrf_tokens[token] == u.id:
            csrf_tokens.pop(token)
            return route_function(request)
        else:
            return error(request, 401)

    return f


def new_csrf_token(request):
    u = current_user(request)
    token = str(uuid.uuid4())
    csrf_tokens[token] = u.id
    return token

