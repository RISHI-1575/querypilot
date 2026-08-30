"""Database helpers for QueryPilot.

Handles building the sample database, reading its schema, and running queries.
Everything here is plain sqlite3 from the standard library.
"""

import os
import sqlite3

# Where the database file lives, and the SQL script that seeds it.
DB_PATH = "querypilot.db"
SEED_PATH = "seed.sql"


def setup_database() -> None:
    """Create the database from seed.sql if it doesn't already exist."""
    if os.path.exists(DB_PATH):
        return

    with open(SEED_PATH, "r") as f:
        script = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(script)
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    """Open a connection to the database."""
    return sqlite3.connect(DB_PATH)


def get_schema(conn: sqlite3.Connection) -> str:
    """Return the CREATE statements for all tables.

    The agent reads this so it knows what tables and columns exist
    before writing any SQL.

    Args:
        conn: An open database connection.

    Returns:
        The schema as a single text block.
    """
    cur = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
    )
    tables = [row[0] for row in cur.fetchall()]
    return "\n\n".join(tables)


def run_query(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    """Run a SQL query and return all rows.

    Raises sqlite3.Error if the query is invalid — the agent uses that
    error message to fix itself and try again.

    Args:
        conn: An open database connection.
        sql: The SQL query to run.

    Returns:
        A list of result rows.
    """
    cur = conn.execute(sql)
    return cur.fetchall()
