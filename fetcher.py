from typing import List

import grequests
import json

from post import parse_data_to_post
from post_storage import Post, PostManager


class DivarFetcher:
    def __init__(self, conn, post_manager: PostManager):
        self.conn = conn
        self.post_manager = post_manager

    async def fetch(self) -> List[Post]:
        resp = await self._get_post_list()
        data = json.loads(resp[0].content)
        tokens = self._get_post_list_tokens(data)
        filtered_tokens = self._filter_out_existing_tokens(tokens)
        print(tokens)
        print(filtered_tokens)
        if filtered_tokens:
            posts = await self._fetch_post_details(filtered_tokens[:1])
            return self._save_posts(posts)
        return []

    async def _get_post_list(self):
        req = grequests.get(
            "https://api.divar.ir/v8/web-search/tehran/rent-apartment/zargandeh?districts=70%2C72&credit=-200000000")
        resp = grequests.map([req])
        return resp

    def _get_post_list_tokens(self, data) -> List[str]:
        tokens = []
        for p in data["web_widgets"]["post_list"]:
            token = p["data"]["action"]["payload"]["token"]
            tokens.append(token)
        return tokens

    async def _fetch_post_details(self, tokens: List[str]) -> List[Post]:
        posts = []
        reqs = (grequests.get(f"https://api.divar.ir/v8/posts-v2/web/{token}") for token in tokens)
        resps = grequests.map(reqs)
        for token, r in zip(tokens, resps):
            data = json.loads(r.content)
            post = parse_data_to_post(token, data)
            posts.append(post)

        headers = {
            'authorization': 'Basic eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiMDk5NTAwMDAwMzUiLCJpc3MiOiJhdXRoIiwiaWF0IjoxNjU3MDI3MzQyLCJleHAiOjE2NTgzMjMzNDIsInZlcmlmaWVkX3RpbWUiOjE2NTcwMjQ3NTMsInVzZXItdHlwZSI6InBlcnNvbmFsIiwidXNlci10eXBlLWZhIjoiXHUwNjdlXHUwNjQ2XHUwNjQ0IFx1MDYzNFx1MDYyZVx1MDYzNVx1MDZjYyIsInNpZCI6ImY3M2Y4ZjM2LWZkNzQtNGI5NC1hMWM0LWM2NmU1ZjY3M2M1NyJ9.89RB8LNElaZyn-bYZtD0RzVErtMenCYa2pwJmUORrAk',
        }

        get_contact_req = (grequests.get(f"https://api.divar.ir/v5/posts/{token}/contact/", headers=headers)
                           for token in tokens)
        get_contact_resp = grequests.map(get_contact_req)
        for p, r in zip(posts, get_contact_resp):
            data = json.loads(r.content)
            phone = data["widgets"]["contact"]["phone"]
            if phone == "(پنهان‌شده؛ چت کنید)":
                p.phone = ""
            else:
                p.phone = phone

        return posts

    def _save_posts(self, posts: List[Post]) -> List[Post]:
        saved_posts = []
        for post in posts:
            p = self.post_manager.create(post)
            saved_posts.append(p)
        return saved_posts

    def _filter_out_existing_tokens(self, tokens: List[str]) -> List[str]:
        cur = self.conn.cursor()

        cur.execute("select token from posts where token in %s;", (tuple(tokens),))
        existing_tokens = set(map(lambda r: r.token, cur.fetchall()))
        new_tokens = set(tokens) - existing_tokens

        self.conn.commit()
        cur.close()

        return list(new_tokens)
