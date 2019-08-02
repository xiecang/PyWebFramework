from time import time

from models.base_model import SQLModel


class Todo(SQLModel):

    sql_create = '''
        CREATE TABLE IF NOT EXISTS `todo` (
            `id`        INT NOT NULL AUTO_INCREMENT,
            `title`     VARCHAR(255) NOT NULL,
            `user_id`   INT NOT NULL,
            PRIMARY KEY (`id`)
        );
    '''

    def __init__(self, form):
        super().__init__(form)
        self.title = form.get('title', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id', None)

    @classmethod
    def add(cls, form, user_id):
        t = Todo(form)
        t.user_id = user_id
        cls.insert(t.__dict__)

    @classmethod
    def update(cls, form):
        todo_id = int(form['id'])
        title = form['title']
        super().update(todo_id, title=title)
