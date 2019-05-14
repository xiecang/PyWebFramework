# -*- coding: utf-8 -*-
import time

from models import Model


class Todo(Model):
    def __init__(self, form, user_id=-1):
        self.id = form.get('id', None)
        self.task = form.get('task', '')
        self.completed = False
        self.user_id = user_id or form.get("user_id")

        self.created_time = form.get('created_time', None)
        self.updated_time = form.get('updated_time', None)
        if self.created_time is None:
            self.created_time = int(time.time())
            self.updated_time = self.created_time

    @classmethod
    def new(cls, form, user_id=-1):
        t = cls(form, user_id)
        return t

    @classmethod
    def update(cls, id, form):
        t = cls.find(id)
        valid_names = [
            'task',
            'completed'
        ]
        for key in form:
            # 这里只应该更新我们想要更新的东西
            if key in valid_names:
                setattr(t, key, form[key])
        t.updated_time = int(time.time())
        t.save()

    @classmethod
    def complete(cls, id: int, completed: bool):
        """
        用法很方便
        Todo.complete(1, True)
        Todo.complete(2, False)
        """
        t = cls.find(id)
        t.completed = completed
        t.save()
        return t

    def is_owner(self, id):
        return self.user_id == id

    def ct(self):
        format_ = '%H:%M:%S'
        value = time.localtime(self.created_time)
        dt = time.strftime(format_, value)
        return dt
