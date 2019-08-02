import pymysql

import secret
import config
from models.base_model import SQLModel
from models.test_model import Test
from models.session import Session
from models.user_role import UserRole
from models.user import User
from models.weibo import Weibo
from models.comment import Comment
from models.todo import Todo


def recreate_table(cursor):
    cursor.execute(Test.sql_create)
    cursor.execute(User.sql_create)
    cursor.execute(Session.sql_create)
    cursor.execute(Weibo.sql_create)
    cursor.execute(Comment.sql_create)
    cursor.execute(Todo.sql_create)


def recreate_database():
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password=secret.mysql_password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'DROP DATABASE IF EXISTS `{}`'.format(
                    config.db_name
                )
            )
            cursor.execute(
                'CREATE DATABASE `{}` DEFAULT CHARACTER SET utf8mb4'.format(
                    config.db_name
                )
            )
            cursor.execute('USE `{}`'.format(config.db_name))

            recreate_table(cursor)

        connection.commit()
    finally:
        connection.close()


def test_data():
    SQLModel.init_db()

    Test.new({})

    # guest user
    form = dict(
        username='guest',
        password='123',
        role=UserRole.normal,
    )
    u, result = User.register(form)

    Session.add(u.id)

    # test todo insert
    form = dict(
        title='test todo',
        user_id=u.id,
    )
    Todo.insert(form)

    # test weibo insert
    form = dict(
        content='test weibo',
        user_id=u.id,
    )
    weibo_id = Weibo.insert(form)

    # test comment insert
    form = dict(
        content='test comment',
        weibo_id=weibo_id,
        user_id=u.id,
    )
    Comment.insert(form)

    SQLModel.connection.close()


if __name__ == '__main__':
    recreate_database()
    test_data()
