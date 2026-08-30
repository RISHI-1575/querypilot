# QueryPilot

Ask questions about your data in plain English and get answers back. QueryPilot
turns the question into SQL, checks it is safe to run, runs it, and fixes its own
query if it fails.

## How it works

```
question -> write sql -> safety check -> run -> (error? retry) -> answer
```

- A local model (via Ollama) writes the SQL from your question.
- The query is checked to make sure it is read-only (only SELECT is allowed).
- If the query errors, the error is fed back to the model and it tries again.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

You also need [Ollama](https://ollama.com) running with a coder model:

```bash
ollama pull qwen3-coder:30b
```

## Run

```bash
.venv/bin/python main.py
```

Then ask things like:

- How many customers are in the South region?
- What is the total revenue per product category?
- Which product has the highest price?

You get the SQL, the rows, a plain-English answer, and a suggested chart type.

## Use your own data

You can load a CSV or Excel file and ask questions about it. Column names are
cleaned and the types are inferred automatically.

```python
import loader
loader.load_file("sales.csv")   # becomes a table you can query
```

## Evaluation

There is a small test set of questions with known-correct SQL. The eval runs the
agent on each and checks the results match.

```bash
.venv/bin/python eval/run_eval.py
```

## Files

- `seed.sql` - sample sales database (customers, products, orders)
- `db.py` - database setup, schema, running queries
- `agent.py` - the agent: writes SQL, safety check, self-correcting loop, explain
- `loader.py` - load CSV / Excel files into the database
- `charts.py` - pick a chart type for a result
- `main.py` - command-line runner
- `eval/` - test set and evaluation script
