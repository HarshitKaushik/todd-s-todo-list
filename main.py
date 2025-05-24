from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal, init_db
from models.models import Task as TaskModel
from schemas.task_schema import TaskCreate, Task


app = FastAPI()


# Initialize the database
init_db()


# Dependency for database session
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


# Need to add authentication & authorisation


@app.post("/task", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):

  task_item = TaskModel(name=task.name, description=task.description, parent_id=task.parent_id, status=False, end_date=None)

  db.add(task_item)
  db.commit()
  db.refresh(task_item)

  return Task.model_validate(task_item)


@app.get("/task/{task_id}", response_model=Task)
async def read_task(task_id: int, db: Session = Depends(get_db)):

  task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  
  return Task.model_validate(task)


@app.put("/task/{task_id}", response_model=Task)
async def update_task(
  task_id: int,
  task_update: Task,
  db: Session = Depends(get_db)
):
  task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")

  task.name = task_update.name
  task.description = task_update.description
  task.parent_id = task_update.parent_id
  task.status = task_update.status

  db.commit()
  db.refresh(task)

  return Task.model_validate(task)


@app.delete("/task/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: Session = Depends(get_db)):

  task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
  subtasks = db.query(TaskModel).filter(TaskModel.parent_id == task_id).all()

  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  
  task.end_date = date.today()
  
  if subtasks:
    for subtask in subtasks:
      subtask.end_date = date.today()

  db.commit()
  
  return {"detail": "Task deleted successfully"}


@app.get("/tasks", response_model=list[Task])
async def read_all_tasks(db: Session = Depends(get_db)):
    
  tasks = db.query(TaskModel).all()
  return [Task.model_validate(task) for task in tasks]


@app.post("/task/{task_id}/subtask", response_model=Task)
async def create_subtask(
    task_id: int,
    subtask: TaskCreate,
    db: Session = Depends(get_db)
):
  parent_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

  if parent_task is None:
    raise HTTPException(status_code=404, detail="Parent task not found")
  
  db_subtask = TaskModel(
    name=subtask.name,
    description=subtask.description,
    parent_id=task_id,
    status=False,
  )
  
  db.add(db_subtask)
  db.commit()
  db.refresh(db_subtask)
  
  return Task.model_validate(db_subtask)


# Get all the subtasks
@app.get("/task/{task_id}/subtasks", response_model=list[Task])
async def read_subtasks(task_id: int, db: Session = Depends(get_db)):
  subtasks = db.query(TaskModel).filter(TaskModel.parent_id == task_id).all()
  return [Task.model_validate(subtask) for subtask in subtasks]


@app.put("/subtask/{subtask_id}", response_model=Task)
async def update_subtask(
  subtask_id: int,
  subtask_update: TaskCreate,
  db: Session = Depends(get_db)
):
  subtask = db.query(TaskModel).filter(TaskModel.id == subtask_id, TaskModel.parent_id != None).first()

  if subtask is None:
    raise HTTPException(status_code=404, detail="Subtask not found")
  
  subtask.name = subtask_update.name
  subtask.description = subtask_update.description
  subtask.status = subtask_update.status

  db.commit()
  db.refresh(subtask)

  return Task.model_validate(subtask)


@app.delete("/subtask/{subtask_id}", response_model=dict)
async def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):

  subtask = db.query(TaskModel).filter(TaskModel.id == subtask_id, TaskModel.parent_id != None).first()

  if subtask is None:
    raise HTTPException(status_code=404, detail="Subtask not found")
  
  subtask.end_date = date.today()
  db.commit()

  return {"detail": "Subtask deleted successfully"}


@app.get("/task/{task_id}/progress")
async def get_task_progress(task_id: int, db: Session = Depends(get_db)):

  task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
  
  if task is None:
    raise HTTPException(status_code=404, detail="Task not found")

  subtasks = db.query(TaskModel).filter(TaskModel.parent_id == task_id).all()

  if not subtasks:  # If no subtasks, determine completion based on some status
    # If the task has an end_date, it's considered complete (100%), otherwise (0%)
    if task.end_date:
      return {"progress": 100}
    else:
      return {"progress": 0}

  else:
    total_subtasks = len(subtasks)
    completed_subtasks = sum(1 for subtask in subtasks if subtask.end_date is not None)

    progress_percentage = (completed_subtasks / total_subtasks) * 100
    return {"progress": progress_percentage}


@app.get("/ping")
async def ping():
  return {"ping": "successful!"}
