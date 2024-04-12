"""Тесты для проверки корректности переноса базы данных."""

import datetime
import sqlite3
import sys
from pathlib import Path

import psycopg2
from contextlib import closing, contextmanager
from dataclasses import fields
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as _connection

sys.path.append("..")

from constants import DSL, RESOURSE_DB, TABLES_TO_CLASSES  # noqa E402

base_path = Path(__file__).resolve().parent.parent


@contextmanager
def conn_context(resource: str):
    sqlite_conn = sqlite3.connect(resource)
    sqlite_conn.row_factory = sqlite3.Row
    yield sqlite_conn
    sqlite_conn.close()


def test_tables_data_summ(
    sqlite_conn: sqlite3.Connection, pg_conn: _connection
):
    """Проверка количества записей в таблицах."""
    for table in TABLES_TO_CLASSES:
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table};")
        sqlite_rows_quantity = sqlite_cursor.fetchone()[0]
        postgres_cursor = pg_conn.cursor()
        postgres_cursor.execute(f"SELECT COUNT(*) FROM {table};")
        postgres_rows_quantity = postgres_cursor.fetchone()[0]  # type: ignore[index]
        assert (
            sqlite_rows_quantity == postgres_rows_quantity
        ), f"Не совпадает коиличество записей в таблицах {table}."


def test_table_data(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Проверка содержания записей в таблицах."""

    for table in TABLES_TO_CLASSES:
        model_fields = fields(TABLES_TO_CLASSES[table])
        sql_column_names = ", ".join(field.name for field in model_fields)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(
            f"SELECT {sql_column_names} FROM {table} ORDER BY ID"
        )
        sqlite_data = sqlite_cursor.fetchall()
        postgres_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        postgres_cursor.execute(f"SELECT * FROM {table} ORDER BY ID")
        postgres_data = postgres_cursor.fetchall()
        for i in range(len(sqlite_data)):
            sqlite_dict = dict(sqlite_data[i])
            for key, value in sqlite_dict.items():
                if key.find("_at") != -1:
                    new_value = str(value) + "00"
                    dt_value = datetime.datetime.strptime(
                        new_value, "%Y-%m-%d %H:%M:%S.%f%z"
                    )
                    sqlite_dict.update({key: dt_value})
            assert set(sqlite_dict.values()) == set(
                postgres_data[i]
            ), f'Есть отличия в таблицах "{table}".'


if __name__ == "__main__":
    with (
        conn_context(base_path / RESOURSE_DB) as sqlite_conn,
        closing(psycopg2.connect(**DSL, cursor_factory=DictCursor)) as pg_conn,
    ):
        test_tables_data_summ(sqlite_conn, pg_conn)
        test_table_data(sqlite_conn, pg_conn)
