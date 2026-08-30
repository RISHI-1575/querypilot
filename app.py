"""Web backend for QueryPilot.

Serves the web page and exposes two endpoints:
  POST /ask     - answer a question
  POST /upload  - load a CSV/Excel file into the database

Run: .venv/bin/uvicorn app:app --reload
"""

import os
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db
import loader
from agent import ask, explain
from charts import pick_chart

app = FastAPI()

# serve the web page assets from the web/ folder
app.mount("/static", StaticFiles(directory="web"), name="static")


class Question(BaseModel):
    question: str
    history: list[dict] = []  # earlier turns: {"q": ..., "sql": ...}


@app.on_event("startup")
def startup() -> None:
    db.setup_database()


@app.get("/")
def home() -> FileResponse:
    return FileResponse("web/index.html")


@app.post("/ask")
def ask_endpoint(payload: Question) -> dict:
    """Answer a question and return the sql, data, chart and a short trace."""
    result = ask(payload.question, payload.history)

    if result["error"]:
        return {
            "error": result["error"],
            "sql": result["sql"],
            "trace": ["wrote SQL", f"stopped: {result['error']}"],
        }

    rows = [list(r) for r in result["rows"]]
    answer = explain(payload.question, result["columns"], result["rows"])
    chart = pick_chart(result["columns"], result["rows"])

    trace = [
        "understood the question",
        "wrote SQL",
        "safety check passed (read-only)",
        f"ran query — {result['attempts']} attempt(s)",
    ]

    return {
        "error": None,
        "sql": result["sql"],
        "columns": result["columns"],
        "rows": rows,
        "answer": answer,
        "chart": chart,
        "trace": trace,
    }


@app.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)) -> dict:
    """Load an uploaded CSV/Excel file into the database as a new table."""
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        table = loader.load_file(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"table": table}
