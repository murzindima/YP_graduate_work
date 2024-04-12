import json
import time
from collections import defaultdict
from typing import Iterable

from asynch import connect
from asynch.connection import Connection
from asynch.cursors import DictCursor
from more_itertools import chunked

from data import PlaybackMarks


async def create_table(client: Connection):
    sql = f"""
        CREATE TABLE IF NOT EXISTS playback_marks (
            timestamp DateTime,
            user_id String,
            movie_id String,
            view_duration Int32
        ) ENGINE = MergeTree()
        ORDER BY timestamp
        """
    async with client.cursor() as cursor:
        await cursor.execute(sql)


async def insert_data(client: Connection, data: Iterable[dict], chunk: int = 1000):
    sql = """
    INSERT INTO playback_marks (timestamp, user_id, movie_id, view_duration)
    VALUES
    """
    async with client.cursor(cursor=DictCursor) as cursor:
        for ch in chunked(data, chunk):
            await cursor.execute(sql, ch)


async def select_data(client: Connection):
    sql = """
    SELECT user_id, avg(view_duration) FROM playback_marks
    GROUP BY user_id
    """
    async with client.cursor() as cursor:
        await cursor.execute(sql)


async def clear_table(client: Connection):
    sql = """
    TRUNCATE TABLE playback_marks
    """
    async with client.cursor() as cursor:
        await cursor.execute(sql)


async def benchmark(data: list[dict], chunk: int, times: int, client: Connection):
    elapsed = defaultdict(list)
    for _ in range(times):
        await clear_table(client)
        start_time = time.time()
        await insert_data(client, data, chunk)
        end_time = time.time()
        elapsed["write"].append(end_time - start_time)

        start_time = time.time()
        await select_data(client)
        end_time = time.time()
        elapsed["read"].append(end_time - start_time)

    return elapsed


async def main():
    client = await connect(
        host="127.0.0.1",
        port=9000,
        database="default",
        user="default",
        password="",
    )
    await create_table(client)
    totals = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    marks = PlaybackMarks(totals[-1], totals[1], totals[0]).to_dict()
    elapsed = dict()
    for total in totals:
        elapsed[total] = await benchmark(marks[: total + 5], 1000, 1, client)

    with open("clickhouse.json", "w") as f:
        json.dump(elapsed, f)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
