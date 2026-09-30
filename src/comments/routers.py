from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from src.comments import controllers
from src.comments.dtos import CommentResponseSchema, CommentSchema
from src.users.models import UserModel
from src.dependencies.is_authenticated import is_authenticated
from src.core.db import get_db
from src.utils.dtos import ResponseSchema

comment_routes = APIRouter(prefix="/tasks", tags=["Comments"])


# =================== CREATE COMMENT ========================
@comment_routes.post(
    "/{task_id}/comments",
    response_model=ResponseSchema[CommentResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: int,
    body: CommentSchema,
    backgroud_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return await controllers.create_comment(body, task_id, backgroud_tasks, db, user)


# ================ GET ALL COMMENTS =====================
@comment_routes.get(
    "/{task_id}/comments",
    response_model=ResponseSchema[list[CommentResponseSchema]],
    status_code=status.HTTP_200_OK,
)
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_task_comments(task_id, db, user)


# ============== UPDATE COMMENT =========================
@comment_routes.put(
    "/{task_id}/comments/{comment_id}",
    response_model=ResponseSchema[CommentResponseSchema],
    status_code=status.HTTP_200_OK,
)
def update_comment(
    task_id: int,
    comment_id: int,
    body: CommentSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.update_comment(
        task_id,
        comment_id,
        body,
        db,
        user,
    )


# =================== DELETE COMMENT ============================
@comment_routes.delete(
    "/{task_id}/comments/{comment_id}",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
def delete_comment(
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.delete_comment(
        task_id,
        comment_id,
        db,
        user,
    )
