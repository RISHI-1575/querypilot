"""Load user files into the database.

Takes a CSV or Excel file, cleans it up a little, and loads it into SQLite
as a new table. After that the agent can query it like any other table.
"""

import os
import re
import sqlite3

import pandas as pd

import db


def clean_name(name: str) -> str:
    """Turn a column or table name into a safe SQL name.

    'Order Date' -> 'order_date', 'Total ($)' -> 'total_'

    Args:
        name: The raw name.

    Returns:
        A lowercase name with only letters, numbers and underscores.
    """
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)  # replace anything odd with _
    return name.strip("_")


def load_file(path: str) -> str:
    """Load a CSV or Excel file into the database as a new table.

    Column names are cleaned and pandas infers the types. The table is named
    after the file.

    Args:
        path: Path to a .csv or .xlsx file.

    Returns:
        The name of the table that was created.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        frame = pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"unsupported file type: {ext}")

    # clean the column names so they are safe to use in SQL
    frame.columns = [clean_name(c) for c in frame.columns]

    table = clean_name(os.path.splitext(os.path.basename(path))[0])

    conn = sqlite3.connect(db.DB_PATH)
    frame.to_sql(table, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    return table


# Quick self-check for the name cleaner. Run: python loader.py
if __name__ == "__main__":
    assert clean_name("Order Date") == "order_date"
    assert clean_name("Total ($)") == "total"
    assert clean_name("customer_id") == "customer_id"
    print("name cleaning checks passed")
