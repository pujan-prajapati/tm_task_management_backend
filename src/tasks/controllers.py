from src.tasks.dtos import TaskSchema
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel
from fastapi import HTTPException


# create task
def create_task(body: TaskSchema, db: Session):
    data = body.model_dump()
    new_task = TaskModel(
        title=data["title"],
        description=data["description"],
        is_completed=data["is_completed"],
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# get all tasks
def get_all_tasks(db: Session):
    tasks = db.query(TaskModel).all()
    return tasks


# get one task
def get_one_task(task_id: int, db: Session):
    task = db.query(TaskModel).get(task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    return task


# update task
def update_task(body: TaskSchema, task_id: int, db: Session):
    task = db.query(TaskModel).get(task_id)
    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    # task.title = body.title
    # task.description = body.description
    # task.is_completed = body.is_completed

    body = body.model_dump()
    for field, value in body.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


# delete task
def delete_task(task_id: int, db: Session):
    task = db.query(TaskModel).get(task_id)
    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    db.delete(task)
    db.commit()

    return None
