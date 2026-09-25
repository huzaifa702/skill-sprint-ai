"""
SkillSprint AI - Database Access & Connection Management
Theme: OnboardVerse | Category: Generative AI PowerPlay

Provides thread-safe SQLite connection management, initialization,
and parameterized execution helpers.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

DATABASE_PATH = os.environ.get(
    "SKILLSPRINT_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "skillsprint.db")
)
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def dict_factory(cursor: sqlite3.Cursor, row: Tuple) -> Dict[str, Any]:
    """Convert SQLite row tuple to a dictionary with column name keys."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection with row factory and FK enabled."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(force_recreate: bool = False):
    """Initialize database tables from schema.sql."""
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    if force_recreate and os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection() as conn:
        conn.executescript(schema_sql)


def query_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return all rows as list of dicts."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()


def query_one(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute a SELECT query and return a single row as dict, or None."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()


def execute_commit(query: str, params: Tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return affected rowcount."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.rowcount


def execute_many(query: str, param_list: List[Tuple]) -> int:
    """Execute batch operations with executemany."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.executemany(query, param_list)
        return cur.rowcount
