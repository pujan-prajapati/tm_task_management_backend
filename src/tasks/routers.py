from fastapi import APIRouter, Depends, status
from src.tasks import controllers
from src.tasks.dtos import TaskSchema, TaskResponseSchema
from src.utils.db import get_db
from src.utils.helpers import is_authenticated
from sqlalchemy.orm import Session
from src.users.models import UserModel
from typing import List

task_routes = APIRouter(prefix="/tasks")


# ============== create task ====================
@task_routes.post(
    "/", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_task(
    body: TaskSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.create_task(body, db, user)


# =================== get all tasks ==================
@task_routes.get(
    "/",
    response_model=List[TaskResponseSchema],
    status_code=status.HTTP_200_OK,
)
def get_all_tasks(
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_all_tasks(db, user)


# =============== get one task =======================
@task_routes.get(
    "/{task_id}", response_model=TaskResponseSchema, status_code=status.HTTP_200_OK
)
def get_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_one_task(task_id, db, user)


# ================= update task ==========================
@task_routes.put(
    "/{task_id}", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED
)
def update_task(
    body: TaskSchema,
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.update_task(body, task_id, db, user)


# ================= delete task ===========================
@task_routes.delete(
    "/{task_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.delete_task(task_id, db, user)
