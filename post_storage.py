from typing import List

import psycopg2


class Post:
    def __init__(
            self, token: str, title: str, description: str, credit: int, rent: float, surface: int, age: int,
            rooms: int, phone: str, additional_phones: List[str], image_count: int,
            *args, **kwargs,
    ):
        self.token: str = token
        self.title: str = title
        self.description: str = description

        self.credit: int = credit
        self.rent: float = rent

        self.surface: int = surface
        self.age: int = age
        self.rooms: int = rooms

        self.phone: str = phone
        self.additional_phone: List[str] = additional_phones

        self.image_count: int = image_count

    @classmethod
    def from_tuple(cls, post_tuple):
        return Post(*post_tuple)

    def to_persian_desc(self):
        return f"{self.title}\n" \
               f"رهن و اجاره: {self.credit}/{self.rent}\n" \
               f"مساحت: {self.surface}\n" \
               f"سن بنا: {self.age}\n" \
               f"اتاق: {self.rooms}\n" \


class PostManager:
    def __init__(self, conn):
        self.conn = conn

    def get_cursor(self):
        cur = self.conn.cursor()
        return cur

    def get_posts_after_token(self, token) -> List[Post]:
        cur = self.get_cursor()

        if token:
            cur.execute(
                "select * from posts "
                "where created_at > (select created_at from posts where posts.token = %s) "
                "order by created_at asc;",
                (token,),
            )
        else:
            cur.execute(
                "select * from posts "
                "order by created_at asc "
                "limit 5;",
                (token,),
            )

        posts = []
        for p in cur.fetchall():
            posts.append(
                Post.from_tuple(p),
            )

        return posts

    def create(self, p: Post):
        with self.get_cursor() as cur:
            print(p.phone)
            cur.execute(
                "insert into posts "
                "(token, title, description, credit, rent, surface, age, rooms, phone, additional_phones, image_count) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "returning *;",
                (p.token, p.title, p.description, p.credit, p.rent, p.surface, p.age, p.rooms, p.phone,
                 p.additional_phone, p.image_count))
            self.conn.commit()
            return Post.from_tuple(cur.fetchone())

    def filter_out_existing(self, tokens: List[str]) -> List[str]:
        with self.get_cursor() as cur:
            cur.execute("select token from posts where token in %s;", (tuple(tokens),))
            existing_tokens = set(map(lambda r: r.token, cur.fetchall()))
            new_tokens = set(tokens) - existing_tokens
            return list(new_tokens)
