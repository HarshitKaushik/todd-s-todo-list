from pydantic import BaseModel, AwareDatetime
from typing import Optional


class TaskBase(BaseModel):
  name: str
  description: Optional[str] = None
  parent_id: Optional[int] = None
  status: bool = False
  end_date: Optional[AwareDatetime] = None


class TaskCreate(TaskBase):
  pass


class Task(TaskBase):
  id: int

  class Config:
    from_attributes = True
