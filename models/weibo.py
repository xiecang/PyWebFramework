from models.base_model import SQLModel
from models.comment import Comment


class Weibo(SQLModel):
    """
    微博类
    """
    sql_create = '''
        CREATE TABLE IF NOT EXISTS `weibo` (
            `id`        INT NOT NULL AUTO_INCREMENT,
            `content`   VARCHAR(255) NOT NULL,
            `user_id`   INT NOT NULL,
            PRIMARY KEY (`id`)
        );
    '''

    def __init__(self, form):
        super().__init__(form)
        self.content = form.get('content', '')
        self.user_id = form.get('user_id', None)

    @classmethod
    def add(cls, form, user_id):
        w = Weibo(form)
        w.user_id = user_id
        # w.save()
        cls.insert(w.__dict__)
        cls.connection.commit()

    def comments(self):
        cs = Comment.all(weibo_id=self.id)
        return cs
