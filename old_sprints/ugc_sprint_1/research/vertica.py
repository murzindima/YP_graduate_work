import json
import time
from collections import defaultdict
from typing import Iterable

import vertica_python
from more_itertools import chunked

from data import PlaybackMarks

connection_info = {
    "host": "127.0.0.1",
    "port": 5433,
    "user": "dbadmin",
    "password": "",
    "autocommit": True,
}

client = vertica_python.connect(**connection_info)


def create_table():
    sql = f"""
        CREATE TABLE IF NOT EXISTS playback_marks (
            timestamp DateTime,
            user_id VARCHAR(256),
            movie_id VARCHAR(256),
            view_duration INTEGER
        )
        """
    cursor = client.cursor()
    cursor.execute(sql)
    cursor.close()


def insert_data(data: Iterable[dict], chunk: int = 1000):
    sql = """
    INSERT INTO playback_marks (timestamp, user_id, movie_id, view_duration)
    VALUES (:timestamp, :user_id, :movie_id, :view_duration)
    """
    cursor = client.cursor()
    for items in chunked(data, chunk):
        cursor.executemany(sql, items, use_prepared_statements=False)
    cursor.close()


def select_data():
    sql = """
    SELECT user_id, avg(view_duration) FROM playback_marks
    GROUP BY user_id
    """
    cursor = client.cursor()
    cursor.execute(sql)
    cursor.close()


def clear_table():
    sql = """
    TRUNCATE TABLE playback_marks
    """
    cursor = client.cursor()
    cursor.execute(sql)
    cursor.close()


def benchmark(data: list[dict], chunk: int, times: int):
    elapsed = defaultdict(list)
    for _ in range(times):
        clear_table()
        start_time = time.time()
        insert_data(data, chunk)
        end_time = time.time()
        elapsed["write"].append(end_time - start_time)

        start_time = time.time()
        select_data()
        end_time = time.time()
        elapsed["read"].append(end_time - start_time)

    return elapsed


if __name__ == "__main__":
    create_table()
    totals = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    marks = PlaybackMarks(totals[-1], totals[1], totals[0]).to_dict()
    elapsed = dict()
    for total in totals:
        elapsed[total] = benchmark(marks[: total + 5], 1000, 1)

    with open("vertica .json", "w") as f:
        json.dump(elapsed, f)
