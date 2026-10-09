"""
Postgres repository.
This is the ONLY file that changed when swapping from in-memory to Postgres.
Service and routes are unchanged — they depend on TaskRepository, not on this class.
"""

from typing import Optional
import psycopg2
import psycopg2.extras
from app.models.task import Task, TaskIn, TaskUpdate
from app.repositories.base import TaskRepository


class PostgresRepository(TaskRepository):

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._init_table()

    def _connect(self):
        return psycopg2.connect(self._dsn)

    def _init_table(self):
        """Create the tasks table if it doesn't exist, and seed it if empty."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id    SERIAL PRIMARY KEY,
                        title TEXT    NOT NULL,
                        done  BOOLEAN NOT NULL DEFAULT FALSE
                    );
                """)
                # Seed only if the table is empty
                cur.execute("SELECT COUNT(*) FROM tasks;")
                count = cur.fetchone()[0]
                if count == 0:
                    cur.executemany(
                        "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                        [
                            ("Buy groceries", False),
                            ("Read FastAPI docs", True),
                            ("Push code to GitHub", False),
                        ]
                    )
            conn.commit()

    def _row_to_task(self, row) -> Task:
        return Task(id=row["id"], title=row["title"], done=row["done"])

    def list_all(self) -> list[Task]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, title, done FROM tasks ORDER BY id;")
                return [self._row_to_task(r) for r in cur.fetchall()]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, title, done FROM tasks WHERE id = %s;",
                    (task_id,)
                )
                row = cur.fetchone()
                return self._row_to_task(row) if row else None

    def create(self, body: TaskIn) -> Task:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                    (body.title, False)
                )
                conn.commit()
                return self._row_to_task(cur.fetchone())

    def update(self, task_id: int, body: TaskUpdate) -> Optional[Task]:
        existing = self.get_by_id(task_id)
        if existing is None:
            return None
        new_title = body.title if body.title is not None else existing.title
        new_done = body.done if body.done is not None else existing.done
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """UPDATE tasks SET title = %s, done = %s
                       WHERE id = %s RETURNING id, title, done;""",
                    (new_title, new_done, task_id)
                )
                conn.commit()
                return self._row_to_task(cur.fetchone())

    def delete(self, task_id: int) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
                conn.commit()
                return cur.rowcount > 0

    def count_stats(self) -> dict:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tasks;")
                total = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM tasks WHERE done = TRUE;")
                done = cur.fetchone()[0]
                return {"total": total, "done": done, "open": total - done}
