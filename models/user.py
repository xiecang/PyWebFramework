from models.base_model import SQLModel
from models.user_role import UserRole

import hashlib

from utils import log


class User(SQLModel):

    sql_create = '''
        CREATE TABLE IF NOT EXISTS `user` (
            `id`        INT NOT NULL AUTO_INCREMENT,
            `username`  VARCHAR(255) NOT NULL,
            `password`  VARCHAR(255) NOT NULL,
            `role`      ENUM('guest', 'normal') NOT NULL,
            PRIMARY KEY (`id`)
        );
    '''

    def __init__(self, form):
        super().__init__(form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.role = form.get('role', UserRole.normal)

    @staticmethod
    def guest():

        form = dict(
            role=UserRole.guest,
            username='【游客】',
        )
        u = User(form)
        return u

    def is_guest(self):
        return self.role == UserRole.guest

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        """$!@><?>HUI&DWQa`"""
        salted = password + salt
        hash = hashlib.sha256(salted.encode()).hexdigest()
        return hash

    @classmethod
    def login(cls, form):
        salted = cls.salted_password(form['password'])
        u = User.one(username=form['username'], password=salted)
        if u is not None:
            result = '登录成功'
            return u, result
        else:
            result = '用户名或者密码错误'
            return User.guest(), result

    @classmethod
    def register(cls, form):
        valid = len(form['username']) > 2 and len(form['password']) > 2
        if valid:
            form['password'] = cls.salted_password(form['password'])
            u = User.new(form)
            result = '注册成功'
            return u, result
        else:
            result = '用户名或者密码长度必须大于2'
            return User.guest(), result

    @classmethod
    def one_for_username_and_password(cls, username, password):
        sql = 'SELECT * FROM {} WHERE username=%s AND password=%s'.format(
            cls.table_name()
        )

        log('ORM one_for_username_and_password', sql)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()

        if result is None:
            return None
        else:
            m = cls(result)
        return m

    @classmethod
    def one_for_id(cls, id):
        sql = 'SELECT * FROM {} WHERE id=%s'.format(
            cls.table_name()
        )

        log('ORM one_for_id', sql)

        with cls.connection.cursor() as cursor:
            cursor.execute(sql, (id,))
            result = cursor.fetchone()

        if result is None:
            return None
        else:
            m = cls(result)
        return m


def t_one():
    SQLModel.init_db()
    one = User.all(role=UserRole.normal)
    log('user one', one)


if __name__ == '__main__':
    t_one()
