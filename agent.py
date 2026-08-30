"""The QueryPilot agent.

Turns a plain-English question into SQL, checks it is safe, runs it, and
retries by feeding the error back to the model if the query fails.

The flow is a simple loop:

    question -> write sql -> safety check -> run -> (error? retry) -> rows
"""

import ollama

import db

# Local model used to write the SQL. Override with the QP_MODEL env var if needed.
import os
MODEL = os.environ.get("QP_MODEL", "qwen3-coder:30b")

# How many times to retry when the query fails.
MAX_RETRIES = 2

# Words that must never appear in a query. We only allow read-only SELECTs.
BANNED_WORDS = [
    "insert", "update", "delete", "drop", "alter",
    "create", "replace", "attach", "pragma",
]


def is_safe(sql: str) -> bool:
    """Check that a query is read-only.

    Only single SELECT (or WITH ... SELECT) statements are allowed. Anything
    that could change the data is rejected.

    Args:
        sql: The SQL query to check.

    Returns:
        True if the query is safe to run.
    """
    q = sql.strip().lower()

    # must start as a read query
    if not (q.startswith("select") or q.startswith("with")):
        return False

    # no stacked statements (one query only)
    if ";" in q.rstrip(";"):
        return False

    # no data-changing keywords
    for word in BANNED_WORDS:
        if word in q:
            return False

    return True


def clean_sql(text: str) -> str:
    """Strip markdown fences the model sometimes adds around the SQL."""
    text = text.strip()
    if text.startswith("```"):
        # drop the first line (``` or ```sql) and the closing fence
        lines = text.splitlines()
        lines = [ln for ln in lines if not ln.startswith("```")]
        text = "\n".join(lines)
    return text.strip()


def generate_sql(schema: str, question: str, error: str | None = None) -> str:
    """Ask the model to write a SQL query for the question.

    If a previous attempt failed, the error is included so the model can fix it.

    Args:
        schema: The database schema (CREATE statements).
        question: The user's question in plain English.
        error: The error from the last attempt, if any.

    Returns:
        The generated SQL query.
    """
    prompt = (
        "You are a SQLite expert. Using the schema below, write ONE read-only "
        "SELECT query that answers the question. Return only the SQL, no "
        "explanation and no markdown.\n\n"
        f"Schema:\n{schema}\n\n"
        f"Question: {question}\n"
    )
    if error:
        prompt += f"\nThe previous query failed with this error: {error}\nFix it."

    resp = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return clean_sql(resp["message"]["content"])


def ask(question: str) -> dict:
    """Answer a question end to end.

    Writes SQL, checks it, runs it, and retries on failure up to MAX_RETRIES.

    Args:
        question: The user's question.

    Returns:
        A dict with keys: sql, rows, error. On success error is None; on
        failure rows is None.
    """
    conn = db.get_connection()
    schema = db.get_schema(conn)

    error = None
    sql = ""

    # try, and retry with the error fed back in
    for attempt in range(MAX_RETRIES + 1):
        sql = generate_sql(schema, question, error)

        if not is_safe(sql):
            conn.close()
            return {"sql": sql, "rows": None, "error": "blocked: not a read-only query"}

        try:
            rows = db.run_query(conn, sql)
            conn.close()
            return {"sql": sql, "rows": rows, "error": None}
        except Exception as e:
            error = str(e)  # loop again and let the model fix it

    conn.close()
    return {"sql": sql, "rows": None, "error": error}


# Quick self-check for the safety guard. Run: python agent.py
if __name__ == "__main__":
    assert is_safe("SELECT * FROM orders")
    assert is_safe("WITH t AS (SELECT 1) SELECT * FROM t")
    assert not is_safe("DROP TABLE orders")
    assert not is_safe("DELETE FROM customers")
    assert not is_safe("SELECT 1; DROP TABLE orders")
    assert not is_safe("update products set price = 0")
    print("guard checks passed")
