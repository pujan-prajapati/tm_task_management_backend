from fastapi import HTTPException, status
from src.tasks.dtos import TaskSchema
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel
from src.users.models import UserModel


# =========== create task =======================
def create_task(body: TaskSchema, db: Session, user: UserModel):
    data = body.model_dump()
    new_task = TaskModel(
        title=data["title"],
        description=data["description"],
        is_completed=data["is_completed"],
        user_id=user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ============== get all tasks =============================
def get_all_tasks(db: Session, user: UserModel):
    tasks = db.query(TaskModel).filter(TaskModel.user_id == user.id).all()
    return tasks


# ============== get one task ===============================
def get_one_task(task_id: int, db: Session, user: UserModel):
    task = db.query(TaskModel).get(task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    return task


# ============== update task ============================
def update_task(body: TaskSchema, task_id: int, db: Session, user: UserModel):
    task = db.query(TaskModel).get(task_id)
    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    # task.title = body.title
    # task.description = body.description
    # task.is_completed = body.is_completed

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    body = body.model_dump()
    for field, value in body.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


# ====================== delete task ================================
def delete_task(task_id: int, db: Session, user: UserModel):
    task = db.query(TaskModel).get(task_id)
    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    db.delete(task)
    db.commit()

    return None
