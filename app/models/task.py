from pydantic import BaseModel, field_validator
from typing import Optional


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskIn(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v.strip() if v else v
