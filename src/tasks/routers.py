from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from src.tasks import controllers
from src.tasks.dtos import (
    TaskSchema,
    TaskResponseSchema,
    AddTagSchema,
    TaskPriority,
    TaskStatus,
    TaskListResponseSchema,
    AssignTaskSchema,
)
from src.users.dtos import UserResponseSchema

from src.users.models import UserModel
from src.core.db import get_db
from src.dependencies.is_authenticated import is_authenticated
from src.utils.dtos import ResponseSchema

task_routes = APIRouter(prefix="/tasks", tags=["Tasks"])


# ============== create task ====================
@task_routes.post(
    "/",
    response_model=ResponseSchema[TaskResponseSchema],
    status_code=status.HTTP_201_CREATED,
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
    response_model=ResponseSchema[TaskListResponseSchema],
    status_code=status.HTTP_200_OK,
)
def get_all_tasks(
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
    search: str | None = None,
    sort_by: str = Query("id"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1, le=100),
    limit: int = Query(10, ge=1, le=100),
    tag_ids: list[int] | None = None,
    priority: TaskPriority | None = None,
    status: TaskStatus | None = None,
    category_id: int | None = None,
):
    return controllers.get_all_tasks(
        db,
        user,
        search,
        sort_by,
        order,
        page,
        limit,
        tag_ids,
        priority,
        status,
        category_id,
    )


# =============== get one task =======================
@task_routes.get(
    "/{task_id}",
    response_model=ResponseSchema[TaskResponseSchema],
    status_code=status.HTTP_200_OK,
)
def get_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_one_task(task_id, db, user)


# ================= update task ==========================
@task_routes.put(
    "/{task_id}",
    response_model=ResponseSchema[TaskResponseSchema],
    status_code=status.HTTP_200_OK,
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
    "/{task_id}",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.delete_task(task_id, db, user)


# ================ ADD TAGS TO TASK ======================
@task_routes.post(
    "/{task_id}/tags",
    response_model=ResponseSchema[TaskResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
def add_tags_to_task(
    task_id: int,
    body: AddTagSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.add_tags_to_task(task_id, body, db, user)


# ================= DELETE TAG FROM TASK ==========================
@task_routes.delete(
    "/{task_id}/tags/{tag_id}",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
def delete_tag_from_task(
    task_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.delete_tag_from_task(task_id, tag_id, db, user)


# ================== ASSIGN TASK TO USER =============================
@task_routes.post(
    "/{task_id}/assign",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def assign_task(
    task_id: int,
    body: AssignTaskSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return await controllers.assign_task(task_id, body, db, user)


# ================== GET TASK ASSIGNEES =============================
@task_routes.get(
    "/{task_id}/assignees",
    response_model=ResponseSchema[list[UserResponseSchema]],
    status_code=status.HTTP_200_OK,
)
def get_task_assignees(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_task_assignees(task_id, db, user)


# ================== REMOVE TASK ASSIGNEE =============================
@task_routes.delete(
    "/{task_id}/assignees/{user_id}",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
def remove_task_assignee(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.remove_task_assignee(task_id, user_id, db, user)
