from typing import List


class User:
    def __init__(self, chat_id: int, last_notified: str | None = None):
        self.chat_id: int = chat_id
        self.last_notified: str | None = last_notified

    @classmethod
    def from_tuple(cls, user_tuple):
        return User(
            *user_tuple
        )


class UserManager:
    def __init__(self, conn):
        self.conn = conn

    def get_cursor(self):
        cur = self.conn.cursor()
        return cur

    def get(self, chat_id: int) -> User | None:
        cur = self.get_cursor()
        cur.execute("select * from users where chat_id=%s", (chat_id,))
        user = cur.fetchone()
        cur.close()

        if user:
            return User.from_tuple(user)
        else:
            return None

    def get_all(self) -> List[User]:
        cur = self.get_cursor()
        cur.execute("select * from users;")

        users = []
        for u in cur.fetchall():
            users.append(
                User.from_tuple(u)
            )
        return users

    def save(self, user: User):
        cur = self.get_cursor()
        cur.execute(
            "update users set last_notified = %s where chat_id=%s returning *;",
            (user.last_notified, user.chat_id),
        )
        self.conn.commit()

        new_user_tuple = cur.fetchone()
        new_user = User.from_tuple(new_user_tuple)

        cur.close()
        return new_user

    def create(self, user: User):
        cur = self.get_cursor()
        cur.execute(
            "insert into users (chat_id, last_notified) values (%s, %s) returning *;",
            (user.chat_id, user.last_notified),
        )
        self.conn.commit()

        new_user_tuple = cur.fetchone()
        new_user = User.from_tuple(new_user_tuple)

        cur.close()
        return new_user
