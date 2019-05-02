# -*- coding: utf-8 -*-
import random

from models.todo import Todo
from utils import log
from models.user import User

# session 可以在服务器端实现过期功能
session = {}


def random_str() -> str:
    """
    生成一个随机的字符串
    """
    seed = 'abcdefjsad89234hdsfkljasdkjghigaksldf89weru'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def template(name: str) -> str:
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def current_user(request) -> str:
    session_id = request.cookies.get('user', '')
    username = session.get(session_id, '【游客】')
    return username


def response_with_headers(
        headers: dict, status_code: int = 200) -> str:
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = f'HTTP/1.1 {status_code} OK\r\n'
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header


def route_login(request) -> bytes:
    headers = {
        'Content-Type': 'text/html',
        # 'Set-Cookie': 'height=169; gua=1; pwd=2; Path=/',
    }
    log('login, cookies', request.cookies)
    username = current_user(request)
    log(f"username: {username}")
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            # 设置一个随机字符串来当令牌使用
            session_id = random_str()
            session[session_id] = u.username
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''  # TODO 此处没有写客户端请求方法为 GET 时的登录成功或失败提示
    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    log('login 的响应', r)
    return r.encode(encoding='utf-8')


def route_register(request) -> bytes:
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        # HTTP BODY 如下
        # username=gw123&password=123
        # 经过 request.form() 函数之后会变成一个字典
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_static(request) -> bytes:
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        img = header + b'\r\n' + f.read()
        return img


def redirect(url: str) -> bytes:
    """
    浏览器在收到 302 响应的时候
    会自动在 HTTP header 里面找 Location 字段并获取一个 url
    然后自动请求新的 url
    """
    headers = {
        'Location': url,
    }
    # 增加 Location 字段并生成 HTTP 响应返回
    # 注意, 没有 HTTP body 部分
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode('utf-8')


def route_profile(request):
    username = current_user(request)
    if username == "【游客】":
        r = redirect('/')
        return r
    u = User.find_by(username=username)
    body = template('profile.html')
    body = body.replace('{{id}}', str(u.id))
    body = body.replace('{{username}}', username)
    body = body.replace('{{note}}', u.note)
    header = response_with_headers({})
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def index(request) -> bytes:
    headers = {
        'Content-Type': 'text/html',
    }
    todo_list = Todo.all()
    todos = []
    for t in todo_list:
        edit_link = f"<a href='/todo/edit?id={t.id}'>编辑</a>"
        delete_link = f"<a href='/todo/delete?id={t.id}'>删除</a>"
        s = f'<h3>{t.id} : {t.title} {edit_link} {delete_link}</h3>'
        todos.append(s)
    todo_html = ''.join(todos)
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def add(request):
    if request.method == 'POST':
        form = request.form()
        t = Todo.new(form)
        t.save()
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/todo')


def update(request):
    if request.method == 'POST':
        form = request.form()
        todo_id = int(form.get("id", -1))
        t = Todo.find_by(id=todo_id)
        t.title = form.get("title", t.title)
        t.save()
    return redirect('/todo')


def edit(request):
    from server import error

    headers = {
        'Content-Type': 'text/html',
    }

    todo_id = int(request.query.get("id", -1))
    if todo_id < 0:
        return error(404)
    t = Todo.find_by(id=todo_id)
    body = template('todo_edit.html')
    body = body.replace('{{todo_id}}', str(t.id))
    body = body.replace('{{todo_title}}', str(t.title))

    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def delete_todo(request):
    from server import error

    todo_id = int(request.query.get("id", -1))
    t = Todo.find_by(id=todo_id)
    if t is not None:
        t.remove()
    return redirect('/todo')


route_dict = {
    '/todo': index,
    "/todo/add": add,
    '/todo/edit': edit,
    '/todo/update': update,
    '/todo/delete': delete_todo,
    #
    '/login': route_login,
    '/register': route_register,
    '/profile': route_profile,
}
