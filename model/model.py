import json
import sqlite3
from spyne import Integer, Unicode
from spyne import ServiceBase, rpc

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    sex INTEGER NOT NULL
)
''')
conn.commit()


class User(object):
    def __init__(self, _id, _user_name, _age, _sex):
        self.id = _id
        self.user_name = _user_name
        self.age = _age
        self.sex = _sex


class Users(object):
    def get_user_list(self, current_page, page_size):
        offset = current_page * page_size
        cursor.execute('SELECT * FROM users LIMIT ? OFFSET ?', (page_size, offset))
        rows = cursor.fetchall()
        return [User(*row) for row in rows]

    def add_user(self, _id, _user_name, _age, _sex):
        if self.query_user(_id) is not None:
            return None
        cursor.execute('INSERT INTO users (id, user_name, age, sex) VALUES (?, ?, ?, ?)', (_id, _user_name, _age, _sex))
        conn.commit()
        return User(_id, _user_name, _age, _sex)

    def edit_user(self, _id, _user_name, _age, _sex):
        if self.query_user(_id) is None:
            return None
        cursor.execute('UPDATE users SET user_name = ?, age = ?, sex = ? WHERE id = ?',
                       (_user_name, _age, _sex, _id))
        conn.commit()
        return self.query_user(_id)

    def delete_user(self, id):
        user = self.query_user(id)
        if user is None:
            return None
        cursor.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        return user

    def query_user(self, _id):
        cursor.execute('SELECT * FROM users WHERE id = ?', (_id,))
        row = cursor.fetchone()
        if row:
            return User(*row)
        return None


user_mgr = Users()


class PyWebService(ServiceBase):
    ...

    @rpc(_returns=Unicode)
    def get_version(self):
        """
        获取系统版本
        :return:
        """
        return json.dumps({'version': 1.0})

    @rpc(Integer, Integer, _returns=Unicode)
    def get_user_list(self, current_page, page_size):
        """
        获取用户列表
        :return:
        """
        return json.dumps(user_mgr.get_user_list(current_page, page_size), default=lambda obj: obj.__dict__)

    @rpc(Integer, Unicode, Integer, Integer, _returns=Unicode)
    def add_user(self, id, user_name, age, sex):
        """
        添加新用户
        :return:
        """
        result = user_mgr.add_user(id, user_name, age, sex)
        if result is None:
            return json.dumps({"error": "id already exists"})
        return json.dumps(result, default=lambda obj: obj.__dict__)

    @rpc(Integer, Unicode, Integer, Integer, _returns=Unicode)
    def edit_user(self, id, user_name, age, sex):
        """
        编辑用户信息
        :return:
        """
        result = user_mgr.edit_user(id, user_name, age, sex)
        if result is None:
            return json.dumps({"error": "user not found"})
        return json.dumps(result, default=lambda obj: obj.__dict__)

    @rpc(Integer, _returns=Unicode)
    def delete_user(self, id):
        """
        删除用户
        :return:
        """
        result = user_mgr.delete_user(id)
        if result is None:
            return json.dumps({"error": "user not found"})
        return json.dumps(result, default=lambda obj: obj.__dict__)

    @rpc(Integer, _returns=Unicode)
    def query_user(self, id):
        """
        查询用户信息
        :return:
        """
        user = user_mgr.query_user(id)
        if user:
            return json.dumps(user, default=lambda obj: obj.__dict__)
        return json.dumps(None)
