# Task API — Week 3 (Postgres + Docker)

CRUD API for tasks. Week 2 ran on an in-memory list. This week the storage is Postgres in Docker, and the whole stack starts with one command.

---

## Start everything

```bash
docker compose up
```

API → `http://localhost:8000`  
Swagger UI → `http://localhost:8000/docs`

Stop and remove containers (data survives in the volume):

```bash
docker compose down
```

---

## What changed from Week 2

**One file changed: `app/repositories/postgres.py`**

The service layer and all routes are identical to Week 2. They depend on the abstract `TaskRepository` interface, not on any concrete implementation. Swapping storage meant writing one new class that implements that interface, then pointing `main.py` at it.

| Layer | Changed? |
|-------|----------|
| Routes (`app/routers/tasks.py`) | ✗ unchanged |
| Models / schemas | ✗ unchanged |
| Abstract repository interface | ✗ unchanged |
| In-memory repository | ✗ kept for reference |
| **Postgres repository** | ✓ new file |
| `main.py` (picks repo based on `DATABASE_URL`) | minor — 2 lines |

---

## Environment

Copy `.env.example` to `.env` before running locally:

```bash
cp .env.example .env
```

`.env` is gitignored. `.env.example` is committed and shows all required variables.

```
DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb
```

---

## Endpoints

| Method | Path | What it does | Status codes |
|--------|------|--------------|-------------|
| GET | `/` | API info + active storage | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks/` | List all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200, 404 |
| POST | `/tasks/` | Create a task | 201, 400 |
| PUT | `/tasks/{id}` | Update a task | 200, 400, 404 |
| DELETE | `/tasks/{id}` | Delete a task | 204, 404 |
| GET | `/stats` | Task counts | 200 |

---

## Sample curl output

```
$ curl -i -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

```
$ curl -i http://localhost:8000/tasks/99

HTTP/1.1 404 Not Found
content-type: application/json

{"detail":"Task 99 not found"}
```

---

## Persistence proof

1. `docker compose up` — API and Postgres start.
2. `POST /tasks/` — create a new task (e.g. id 4).
3. `docker compose down` — stops and removes both containers.
4. `docker compose up` — starts again.
5. `GET /tasks/` — task id 4 is still there.

Data survives because Postgres writes to a **named Docker volume** (`postgres_data`). The volume is not removed by `docker compose down` — only `docker compose down -v` removes it. That's the difference between a demo and a real service.

---

## Project structure

```
.
├── app/
│   ├── models/
│   │   └── task.py          # Pydantic schemas
│   ├── repositories/
│   │   ├── base.py          # Abstract interface (TaskRepository)
│   │   ├── memory.py        # Week 2 implementation — kept for reference
│   │   └── postgres.py      # Week 3 implementation — the only new file
│   └── routers/
│       └── tasks.py         # Routes — unchanged from Week 2
├── main.py                  # App entry point — picks repo from DATABASE_URL
├── init.sql                 # Creates table + seeds data on first run
├── docker-compose.yml       # App + Postgres, one command
├── Dockerfile
├── requirements.txt
├── .env.example             # Committed — shows required vars
├── .env                     # Gitignored — real values
└── .gitignore
```

---

## Commit log

```
Stage 0: hello server
Stage 1: root and health endpoints
Stage 2: read endpoints with 404
Stage 3: create with validation
Stage 4: full CRUD
Stage 5: Swagger UI
Stage 6: publish and docs
Stage 7: postgres repository + docker compose
```
