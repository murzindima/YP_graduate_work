"""Заполнение БД из файла."""
import sqlite3
from contextlib import closing, contextmanager
from dataclasses import astuple, fields
from datetime import datetime

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from constants import (
    COLUMN_NAME_CORRESPONDENCE,
    DSL,
    RESOURSE_DB,
    TABLES_TO_CLASSES,
    UPLOAD_SIZE,
)


class SQLiteExtractor:
    """Класс-метод извлечения из БД sqlite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def extract_data(self, table, model):
        cursor = self.connection.cursor()
        cursor.row_factory = sqlite3.Row
        column_names = ", ".join(field.name for field in fields(model))
        cursor.execute(f"SELECT {column_names} FROM {table}")
        while records := cursor.fetchmany(UPLOAD_SIZE):
            yield [model(**dict(record)) for record in records]


class PostgresSaver:
    """Класс-метод сохранения в БД Postgress."""

    def __init__(self, connection: _connection):
        self.conn = connection

    def save_all_data(self, table, model, rows):
        with self.conn.cursor() as curs:
            column_names = ", ".join(
                COLUMN_NAME_CORRESPONDENCE[field.name]
                for field in fields(model)
            )
            template = ", ".join(["%s"] * len(fields(model)))
            res = ", ".join(
                curs.mogrify(f"({template})", astuple(row)).decode("utf-8")
                for row in rows
            )
            query = (
                f"INSERT INTO content.{table} ({column_names})"
                f" VALUES {res} ON CONFLICT (id) DO NOTHING;"
            )
            curs.execute(query)
            self.conn.commit()


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres."""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(sqlite_conn)

    for table, model in TABLES_TO_CLASSES.items():
        for rows in sqlite_extractor.extract_data(table=table, model=model):
            postgres_saver.save_all_data(table=table, model=model, rows=rows)


@contextmanager
def conn_context(resource: str):
    sqlite3.register_converter(
        "timestamp",
        lambda x: datetime.fromisoformat(x.decode() + ":00"),
    )
    sqlite_conn = sqlite3.connect(
        resource, detect_types=sqlite3.PARSE_DECLTYPES
    )
    yield sqlite_conn
    sqlite_conn.close()


if __name__ == "__main__":
    with (
        conn_context(RESOURSE_DB) as sqlite_conn,
        closing(psycopg2.connect(**DSL, cursor_factory=DictCursor)) as pg_conn,
    ):
        load_from_sqlite(sqlite_conn, pg_conn)
