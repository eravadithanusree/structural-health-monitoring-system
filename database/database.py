"""
Database access layer for SHMS.

All SQL lives here so the rest of the app never writes raw queries.
Uses sqlite3's Row factory so records behave like dicts.
"""

import sqlite3
from contextlib import contextmanager

from config import Config


def init_db():
    """Create tables from schema.sql if they don't already exist."""
    with open(Config.SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_connection():
    """Context-managed connection so callers never leak handles."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_reading(vibration, strain, temperature, status, confidence, structure_id="default"):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO readings (structure_id, vibration, strain, temperature, status, confidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (structure_id, vibration, strain, temperature, status, confidence),
        )
        return cur.lastrowid


def get_latest_reading(structure_id="default"):
    with get_connection() as conn:
        row = conn.execute(
            """SELECT * FROM readings WHERE structure_id = ?
               ORDER BY id DESC LIMIT 1""",
            (structure_id,),
        ).fetchone()
        return dict(row) if row else None


def get_history(structure_id="default", limit=50, offset=0):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM readings WHERE structure_id = ?
               ORDER BY id DESC LIMIT ? OFFSET ?""",
            (structure_id, limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]


def get_history_count(structure_id="default"):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as c FROM readings WHERE structure_id = ?",
            (structure_id,),
        ).fetchone()
        return row["c"]


def get_recent_series(structure_id="default", limit=30):
    """Chronological (oldest->newest) slice for charting."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM (
                    SELECT * FROM readings WHERE structure_id = ?
                    ORDER BY id DESC LIMIT ?
               ) sub ORDER BY sub.id ASC""",
            (structure_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_structures():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM structures ORDER BY name").fetchall()
        return [dict(r) for r in rows]
