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

## Screenshots

The web app is a chat. You ask a question, it replies, and it remembers the
earlier turns so follow-ups work.

Ask a question and get a plain-English answer with the data:

![answer](docs/2-answer.png)

Follow-up questions use the previous message for context (here "what about the
North region?" after asking about the South):

![follow up](docs/3-followup.png)

When the result fits a chart, it draws one:

![chart](docs/4-chart.png)

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

You also need [Ollama](https://ollama.com) running with a coder model:

```bash
ollama pull qwen3-coder:30b
```

## Run the web app

```bash
.venv/bin/uvicorn app:app
```

Then open http://127.0.0.1:8000 and ask a question. You get a plain-English
answer, a chart, the data table, the SQL, and a short trace of what the agent did.

## Run in the terminal

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

Latest run: 17/18 correct (94%) on the test set.

The one miss read "average order value" as a median instead of a mean. The SQL
ran fine, it was just the wrong reading of the question, so the self-correction
retry (which fixes broken queries) does not help there. On this data the model
rarely writes broken SQL, so self-correction acts as a safety net rather than
something that lifts the score.

## Files

- `seed.sql` - sample sales database (customers, products, orders)
- `db.py` - database setup, schema, running queries
- `agent.py` - the agent: writes SQL, safety check, self-correcting loop, explain
- `loader.py` - load CSV / Excel files into the database
- `charts.py` - pick a chart type for a result
- `main.py` - command-line runner
- `app.py` - web backend (FastAPI)
- `web/` - the web page (HTML, CSS, JS)
- `eval/` - test set and evaluation script
