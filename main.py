"""
Task API — Week 3
FastAPI + Postgres (Docker) · in-memory fallback for local dev without Docker
"""

import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Task API",
    description="CRUD API for tasks — Postgres backend, in-memory fallback.",
    version="2.0",
)

# ── Repository selection ──────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    from app.repositories.postgres import PostgresRepository
    _repo = PostgresRepository(dsn=DATABASE_URL)
else:
    from app.repositories.memory import InMemoryRepository
    _repo = InMemoryRepository()

# ── Inject repository into router ─────────────────────────────────────────────
from app.routers import tasks as tasks_router
tasks_router._repo_instance = _repo

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers.tasks import router as tasks_rt
app.include_router(tasks_rt)

# ── Utility endpoints ─────────────────────────────────────────────────────────

@app.get("/", summary="API info")
def root():
    storage = "postgres" if DATABASE_URL else "in-memory"
    return {"name": "Task API", "version": "2.0", "storage": storage, "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/stats", summary="Task statistics")
def stats():
    return _repo.count_stats()


@app.post("/reset", summary="Reset seed data (in-memory only)")
def reset():
    if DATABASE_URL:
        return {"message": "Reset is only available in in-memory mode."}
    from app.repositories.memory import SEED
    _repo._tasks = [t.model_copy() for t in SEED]
    _repo._next_id = 4
    return {"message": "Reset to seed data", "tasks": [t.model_dump() for t in _repo._tasks]}
