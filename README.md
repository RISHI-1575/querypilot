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

- Which region has the most customers?
- What is the total revenue per product category?
- Show the top 3 products by quantity sold.

## Files

- `seed.sql` - sample sales database (customers, products, orders)
- `db.py` - database setup, schema, running queries
- `agent.py` - the agent: writes SQL, safety check, self-correcting loop
- `main.py` - command-line runner
