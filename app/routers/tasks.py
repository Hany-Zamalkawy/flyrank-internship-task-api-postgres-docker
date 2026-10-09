"""
Task router — unchanged from Week 2.
Depends on TaskRepository (the abstract interface), not on any concrete implementation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.task import Task, TaskIn, TaskUpdate
from app.repositories.base import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Set by main.py at startup via: tasks_router._repo_instance = repo
_repo_instance: Optional[TaskRepository] = None


def get_repo() -> TaskRepository:
    """Returns the active repository. Set by main.py at startup."""
    if _repo_instance is None:
        raise RuntimeError("Repository not configured")
    return _repo_instance


@router.get("/", summary="List all tasks", response_model=list[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)):
    return repo.list_all()


@router.get("/{task_id}", summary="Get one task", response_model=Task)
def get_task(task_id: int, repo: TaskRepository = Depends(get_repo)):
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.post("/", status_code=201, summary="Create a task", response_model=Task)
def create_task(body: TaskIn, repo: TaskRepository = Depends(get_repo)):
    return repo.create(body)


@router.put("/{task_id}", summary="Update a task", response_model=Task)
def update_task(task_id: int, body: TaskUpdate, repo: TaskRepository = Depends(get_repo)):
    if body.title is None and body.done is None:
        raise HTTPException(status_code=400, detail="Body must include title or done")
    task = repo.update(task_id, body)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.delete("/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int, repo: TaskRepository = Depends(get_repo)):
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
