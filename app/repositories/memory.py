"""
In-memory repository (Week 2 implementation).
Kept here to show what the Postgres repository replaced.
The service and routes never imported this directly — they used TaskRepository.
"""

from typing import Optional
from app.models.task import Task, TaskIn, TaskUpdate
from app.repositories.base import TaskRepository

SEED = [
    Task(id=1, title="Buy groceries", done=False),
    Task(id=2, title="Read FastAPI docs", done=True),
    Task(id=3, title="Push code to GitHub", done=False),
]


class InMemoryRepository(TaskRepository):

    def __init__(self):
        self._tasks: list[Task] = [t.model_copy() for t in SEED]
        self._next_id: int = 4

    def list_all(self) -> list[Task]:
        return list(self._tasks)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def create(self, body: TaskIn) -> Task:
        task = Task(id=self._next_id, title=body.title, done=False)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def update(self, task_id: int, body: TaskUpdate) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if task is None:
            return None
        if body.title is not None:
            task.title = body.title
        if body.done is not None:
            task.done = body.done
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task is None:
            return False
        self._tasks.remove(task)
        return True

    def count_stats(self) -> dict:
        done = sum(1 for t in self._tasks if t.done)
        return {"total": len(self._tasks), "done": done, "open": len(self._tasks) - done}
