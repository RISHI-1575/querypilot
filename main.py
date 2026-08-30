"""Command-line runner for QueryPilot.

Type a question, see the SQL the agent wrote and the answer. Type 'exit' to quit.
"""

import db
from agent import ask


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
        else:
            for row in result["rows"]:
                print(row)
            print()


if __name__ == "__main__":
    main()
