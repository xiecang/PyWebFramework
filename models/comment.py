from models.base_model import SQLModel
from models.user import User
# from models.weibo import Weibo


class Comment(SQLModel):
    """
    评论类
    """
    sql_create = '''
        CREATE TABLE IF NOT EXISTS `comment` (
            `id`        INT NOT NULL AUTO_INCREMENT,
            `content`   VARCHAR(255) NOT NULL,
            `user_id`   INT NOT NULL,
            `weibo_id`  INT NOT NULL,
            PRIMARY KEY (`id`)
        );
    '''

    def __init__(self, form, user_id=-1):
        super().__init__(form)
        self.content = form.get('content', '')
        self.user_id = form.get('user_id', user_id)
        self.weibo_id = int(form.get('weibo_id', -1))

    def user(self):
        # u = User.find_by(id=self.user_id)
        u = User.one(id=self.user_id)
        return u
