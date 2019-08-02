from models.todo import Todo
from routes import (
    redirect,
    current_user,
    html_response,
    login_required,
    csrf_required,
    new_csrf_token,
)
from utils import log


def index(request):
    """
    todo 首页的路由函数
    """
    u = current_user(request)
    todos = Todo.all(user_id=u.id)
    token = new_csrf_token(request)
    return html_response('todo_index.html', todos=todos, token=token)


def add(request):
    u = current_user(request)
    form = request.form()
    Todo.add(form, u.id)
    return redirect('/todo/index')


def delete(request):
    todo_id = int(request.query['id'])
    Todo.delete(todo_id)
    return redirect('/todo/index')


def edit(request):
    todo_id = int(request.query['id'])
    t = Todo.one(id=todo_id)
    token = new_csrf_token(request)
    return html_response('todo_edit.html', todo=t, token=token)


def update(request):
    form = request.form()
    Todo.update(form)
    return redirect('/todo/index')


def same_user_required(route_function):
    def f(request):
        log('same_user_required')
        u = current_user(request)
        if 'id' in request.query:
            todo_id = request.query['id']
        else:
            todo_id = request.form()['id']
        t = Todo.one(id=int(todo_id))

        if t.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/todo/index')

    return f


def route_dict():
    d = {
        '/todo/add': login_required(add),
        '/todo/delete': csrf_required(login_required(same_user_required(delete))),
        '/todo/edit': login_required(same_user_required(edit)),
        '/todo/update': csrf_required(login_required(same_user_required(update))),
        '/todo/index': login_required(index),
    }
    return d
