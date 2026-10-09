"""
Abstract repository interface.
Both InMemoryRepository and PostgresRepository implement this.
Service and routes depend only on this interface — never on a concrete implementation.
That's how swapping storage changes exactly one file.
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.models.task import Task, TaskIn, TaskUpdate


class TaskRepository(ABC):

    @abstractmethod
    def list_all(self) -> list[Task]:
        ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        ...

    @abstractmethod
    def create(self, body: TaskIn) -> Task:
        ...

    @abstractmethod
    def update(self, task_id: int, body: TaskUpdate) -> Optional[Task]:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    def count_stats(self) -> dict:
        ...
