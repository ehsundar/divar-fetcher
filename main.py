import logging
import os
import re
import sys
import time

import psycopg2
from psycopg2.extras import NamedTupleCursor

from bot import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.basicConfig(level=logging.DEBUG)


def main():
    conn = psycopg2.connect("postgresql://postgres:postgres@db/postgres", cursor_factory=NamedTupleCursor)
    TelegramBot(conn)


def run_migrations():
    time.sleep(1)
    conn = psycopg2.connect("postgresql://postgres:postgres@db/postgres", cursor_factory=NamedTupleCursor)

    pat = re.compile(r"\d+_.*.up.sql")
    files = os.listdir("migrations")
    filtered_files = filter(pat.match, files)
    for file in sorted(filtered_files):
        print(f"running migration: {file}", flush=True)
        with open(f"migrations/{file}", "r") as f:
            with conn.cursor() as cur:
                cur.execute(f.read())
                conn.commit()


if __name__ == "__main__":
    match sys.argv[1]:
        case "migrate":
            run_migrations()
        case "bot":
            main()
        case _:
            print("must specify command")
