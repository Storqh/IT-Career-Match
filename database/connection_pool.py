"""
Database Connection Pool - psycopg_pool for production-ready connection management
"""
import os
import threading
from contextlib import contextmanager
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from config import get_config


# Global pool instance (thread-safe)
_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_db_pool(database_url: str = None, min_size: int = 2, max_size: int = 10) -> ConnectionPool:
    """
    Get or create global connection pool.

    Args:
        database_url: PostgreSQL connection string. If None, uses config.
        min_size: Minimum connections in pool
        max_size: Maximum connections in pool

    Returns:
        ConnectionPool instance
    """
    global _pool

    if _pool is not None:
        return _pool

    with _pool_lock:
        if _pool is not None:
            return _pool

        if database_url is None:
            config = get_config()
            database_url = config.DATABASE_URL

        if not database_url:
            raise ValueError("DATABASE_URL not configured")

        # Create pool with kwargs for psycopg3
        # autocommit=False (default) to allow explicit transaction control
        _pool = ConnectionPool(
            conninfo=database_url,
            min_size=min_size,
            max_size=max_size,
            kwargs={
                "row_factory": dict_row,
                "autocommit": False,
            },
            # Pool configuration
            timeout=30,  # seconds to wait for connection
            max_idle=300,  # seconds before closing idle connection
            max_lifetime=3600,  # seconds before recycling connection
        )

        # Wait for pool to be ready
        _pool.wait()

        print(f"[DB] Connection pool created: min={min_size}, max={max_size}")
        return _pool


def close_db_pool():
    """Close the global connection pool."""
    global _pool

    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None
            print("[DB] Connection pool closed")


@contextmanager
def get_connection():
    """
    Context manager to get a connection from the pool.
    Automatically returns connection to pool after use.

    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
                users = cur.fetchall()
    """
    pool = get_db_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager to get a cursor directly.

    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
        else:
            # With autocommit=False, we need to rollback for read-only transactions
            # to release any locks
            conn.rollback()


# Backward compatibility functions
def get_db_connection():
    """
    DEPRECATED: Use get_connection() context manager instead.
    Returns a connection that MUST be manually returned to pool.
    """
    pool = get_db_pool()
    return pool.getconn()


def return_db_connection(conn):
    """DEPRECATED: Return connection to pool."""
    pool = get_db_pool()
    pool.putconn(conn)


def init_db_pool(app=None):
    """Initialize pool for Flask app."""
    if app:
        database_url = app.config.get("DATABASE_URL")
        min_size = app.config.get("DB_POOL_MIN", 2)
        max_size = app.config.get("DB_POOL_MAX", 10)
    else:
        config = get_config()
        database_url = config.DATABASE_URL
        min_size = 2
        max_size = 10

    return get_db_pool(database_url, min_size, max_size)


# Health check
def check_db_connection() -> bool:
    """Check if database is accessible."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() is not None
    except Exception as e:
        print(f"[DB] Health check failed: {e}")
        return False


# For testing - create test pool with SQLite
def get_test_pool(database_url: str = "sqlite:///:memory:") -> ConnectionPool:
    """Create a test pool (for testing only)."""
    # Note: psycopg_pool doesn't support SQLite
    # This is a placeholder for when we add SQLite support
    raise NotImplementedError("Test pool not implemented - use PostgreSQL test container")


if __name__ == "__main__":
    # Test pool creation
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from dotenv import load_dotenv
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        pool = get_db_pool(database_url, min_size=1, max_size=3)
        print(f"Pool stats: {pool.get_stats()}")

        with get_cursor() as cur:
            cur.execute("SELECT version()")
            print(f"PostgreSQL: {cur.fetchone()}")

        close_db_pool()
    else:
        print("DATABASE_URL not set")