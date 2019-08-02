from models.comment import Comment
from models.user import User
from models.weibo import Weibo
from routes import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from utils import log


def index(request):
    """
    weibo 首页的路由函数
    """
    u = current_user(request)
    # weibos = Weibo.all(user_id=u.id)
    weibos = (
        Weibo.select(Weibo.connection)
        .where(user_id=u.id)
        .all()
    )
    return html_response('weibo_index.html', weibos=weibos, user=u)


def add(request):
    """
    用于增加新 weibo 的路由函数
    """
    u = current_user(request)
    form = request.form()
    Weibo.add(form, u.id)
    return redirect('/weibo/index')


def delete(request):
    """
    用于删除 weibo 的路由函数
    """
    weibo_id = int(request.query['id'])
    Weibo.delete(weibo_id)
    cs = Comment.all(weibo_id=weibo_id)
    for c in cs:
        c.delete(c.id)
    return redirect('/weibo/index')


def edit(request):
    weibo_id = int(request.query['id'])
    w = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


def update(request):
    """
    用于更新 weibo 的路由函数
    """
    form = request.form()
    weibo_id = form.pop('id')
    Weibo.update(weibo_id, **form)
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    form = request.form()
    weibo_id = int(form['weibo_id'])

    c = Comment(form)
    c.user_id = u.id
    c.weibo_id = weibo_id
    Comment.insert(c.__dict__)

    log('comment add', c, u, form)
    return redirect('/weibo/index')


def comment_delete(request):
    # 请求数据
    u = current_user(request)
    comment_id = int(request.query['id'])

    # 评论及对应微博
    c = Comment.one(id=comment_id)
    w = Weibo.one(id=c.weibo_id)

    # 是否为评论者或博主
    comment_owner = u.id == c.user_id
    weibo_owner = u.id == w.user_id

    if comment_owner or weibo_owner:
        # 删除
        Comment.delete(comment_id)
        return redirect('/weibo/index')
    else:
        return redirect('/weibo/index')


def comment_edit(request):
    comment_id = int(request.query['id'])
    c = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=c)


def comment_update(request):
    form = request.form()
    id = form.pop('id')
    Comment.update(id, **form)
    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        if 'id' in request.query:
            weibo_id = request.query['id']
        else:
            weibo_id = request.form()['id']
        w = Weibo.one(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            comment_id = request.form()['id']
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')
    return f


def route_dict():
    d = {
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(weibo_owner_required(delete)),
        '/weibo/edit': login_required(weibo_owner_required(edit)),
        '/weibo/update': login_required(weibo_owner_required(update)),
        '/weibo/index': login_required(index),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/delete': login_required(comment_delete),
        '/comment/edit': login_required(comment_owner_required(comment_edit)),
        '/comment/update': login_required(
            comment_owner_required(comment_update)
        ),
    }
    return d
