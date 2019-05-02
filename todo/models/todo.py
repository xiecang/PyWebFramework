# -*- coding: utf-8 -*-
from models import Model


class Todo(Model):
    def __init__(self, form):
        self.id = form.get('id', None)
        self.title = form.get('title', '')
        # 还应该增加 时间 等数据
