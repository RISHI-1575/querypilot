"""Pick a chart type for a query result.

Simple rules, no model needed. Looks at the shape of the result and the
column names to guess the best way to show it.
"""

# column names that usually mean "time" -> good for a line chart
TIME_HINTS = ["date", "month", "year", "day", "time", "quarter", "week"]


def is_number(value) -> bool:
    """Return True if the value is a number (int or float, not bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def pick_chart(columns: list[str], rows: list[tuple]) -> str:
    """Choose a chart type for the result.

    Args:
        columns: The result column names.
        rows: The result rows.

    Returns:
        One of: 'kpi', 'line', 'pie', 'bar', 'table'.
    """
    if not rows or not columns:
        return "table"

    # a single number -> show it big as a KPI
    if len(rows) == 1 and len(columns) == 1 and is_number(rows[0][0]):
        return "kpi"

    # two columns where the second is a number -> a real chart
    if len(columns) == 2 and is_number(rows[0][1]):
        label = columns[0].lower()

        # a time-like label reads best as a line
        if any(hint in label for hint in TIME_HINTS):
            return "line"

        # only a few categories -> pie, otherwise bar
        return "pie" if len(rows) <= 6 else "bar"

    # anything else -> just a table
    return "table"


# Quick self-check. Run: python charts.py
if __name__ == "__main__":
    assert pick_chart(["total"], [(500,)]) == "kpi"
    assert pick_chart(["month", "sales"], [("2024-01", 10), ("2024-02", 20)]) == "line"
    assert pick_chart(["region", "sales"], [("N", 5), ("S", 7)]) == "pie"
    assert pick_chart(["name", "qty"], [(str(i), i) for i in range(10)]) == "bar"
    assert pick_chart(["a", "b", "c"], [(1, 2, 3)]) == "table"
    print("chart checks passed")
