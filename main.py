"""Command-line runner for QueryPilot.

Type a question, see the SQL the agent wrote and the answer. Type 'exit' to quit.
"""

import db
from agent import ask, explain
from charts import pick_chart


def main() -> None:
    db.setup_database()
    print("QueryPilot — ask a question about the sales data ('exit' to quit)\n")

    while True:
        question = input("> ").strip()
        if question.lower() in ("exit", "quit", ""):
            break

        result = ask(question)

        print("\nSQL:", result["sql"])
        if result["error"]:
            print("Error:", result["error"], "\n")
            continue

        for row in result["rows"]:
            print(row)

        answer = explain(question, result["columns"], result["rows"])
        chart = pick_chart(result["columns"], result["rows"])
        print("\nAnswer:", answer)
        print("Chart:", chart, "\n")


if __name__ == "__main__":
    main()
