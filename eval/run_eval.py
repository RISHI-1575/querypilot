"""Evaluate QueryPilot on a test set.

For each question we have a reference SQL query (the correct answer). We run
the agent, run the reference, and check the results match. We also report how
many questions needed a retry, which shows the self-correction loop working.

Run: .venv/bin/python eval/run_eval.py
"""

import json
import os
import sys

# let this file import the project modules from the parent folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from agent import ask

TESTSET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testset.json")


def result_matches(expected: list[tuple], got: list[tuple]) -> bool:
    """Compare two result sets, ignoring row order."""
    if got is None:
        return False
    return set(expected) == set(got)


def main() -> None:
    db.setup_database()

    with open(TESTSET_PATH) as f:
        testset = json.load(f)

    conn = db.get_connection()

    correct = 0
    needed_retry = 0

    for item in testset:
        question = item["question"]
        expected, _ = db.run_query(conn, item["sql"])

        result = ask(question)
        ok = result_matches(expected, result["rows"])

        if ok:
            correct += 1
        if result["attempts"] > 1:
            needed_retry += 1

        mark = "ok " if ok else "X  "
        print(f"{mark} (tries={result['attempts']}) {question}")

    conn.close()

    total = len(testset)
    print("\n--- results ---")
    print(f"accuracy: {correct}/{total} = {correct / total:.0%}")
    print(f"needed a retry: {needed_retry}/{total}")


if __name__ == "__main__":
    main()
