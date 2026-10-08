"""Postgres access."""
import os

import psycopg
from psycopg.rows import dict_row


def url():
    return os.environ.get("DATABASE_URL", "")


def connect():
    return psycopg.connect(url(), row_factory=dict_row)


def query(sql, params=None, fetch=True):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params or ())
        if not fetch or cur.description is None:
            return []
        return cur.fetchall()


def one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None
