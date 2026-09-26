"""
SkillSprint AI - Database Access & Connection Management
Theme: OnboardVerse | Category: Generative AI PowerPlay

Provides thread-safe SQLite connection management, initialization,
and parameterized execution helpers.
"""

import sqlite3
import os
import shutil
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLED_DB = os.path.join(BASE_DIR, "skillsprint.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def resolve_db_path() -> str:
    """
    Resolve the working SQLite database path.
    On serverless platforms (e.g. Vercel, AWS Lambda), the deployment directory is read-only.
    To support full write operations (audit logs, evaluations, user sessions, plan generation),
    we copy the bundled SQLite database to /tmp/skillsprint.db if the local directory is read-only
    or running inside Vercel.
    """
    env_path = os.environ.get("SKILLSPRINT_DB_PATH")
    if env_path:
        return env_path

    # Detect serverless or read-only environment
    is_serverless = bool(
        os.environ.get("VERCEL")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or (os.path.exists("/tmp") and not os.access(BASE_DIR, os.W_OK))
    )

    if is_serverless:
        tmp_db = "/tmp/skillsprint.db"
        try:
            # If tmp_db does not exist or bundled_db has content while tmp_db is empty, copy bundled
            if not os.path.exists(tmp_db) or (
                os.path.exists(BUNDLED_DB) and os.path.getsize(tmp_db) == 0
            ):
                if os.path.exists(BUNDLED_DB):
                    shutil.copy2(BUNDLED_DB, tmp_db)
            if os.path.exists(tmp_db):
                return tmp_db
        except Exception as e:
            print(f"[SkillSprint DB] Failed to mirror database to /tmp: {e}")
            if os.path.exists(BUNDLED_DB):
                return BUNDLED_DB

    return BUNDLED_DB


DATABASE_PATH = resolve_db_path()


def get_database_path() -> str:
    """Return the currently active database path."""
    return resolve_db_path()


def dict_factory(cursor: sqlite3.Cursor, row: Tuple) -> Dict[str, Any]:
    """Convert SQLite row tuple to a dictionary with column name keys."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


_seeding_lock = False


@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection with row factory and safe pragmas."""
    global _seeding_lock
    db_path = resolve_db_path()

    # Self-heal: If database doesn't exist or is empty, copy from bundled or seed
    if not _seeding_lock and (not os.path.exists(db_path) or os.path.getsize(db_path) == 0):
        _seeding_lock = True
        try:
            if os.path.exists(BUNDLED_DB) and db_path != BUNDLED_DB:
                shutil.copy2(BUNDLED_DB, db_path)
            else:
                from src.database.seed_data import seed_database
                seed_database()
        except Exception as err:
            print(f"[SkillSprint DB] Auto-initialization error: {err}")
        finally:
            _seeding_lock = False

    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = dict_factory

    # Safe pragmas that don't crash if read-only or unsupported
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass

    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        try:
            conn.execute("PRAGMA journal_mode = DELETE;")
        except Exception:
            pass

    try:
        yield conn
        try:
            conn.commit()
        except Exception:
            pass
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


def init_db(force_recreate: bool = False):
    """Initialize database tables from schema.sql."""
    db_path = resolve_db_path()
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection() as conn:
        if force_recreate:
            conn.execute("PRAGMA foreign_keys = OFF;")
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r["name"] if isinstance(r, dict) else r[0] for r in cur.fetchall()]
            for t in tables:
                if not t.startswith("sqlite_"):
                    cur.execute(f"DROP TABLE IF EXISTS {t};")
            conn.execute("PRAGMA foreign_keys = ON;")
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
