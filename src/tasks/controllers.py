from fastapi import HTTPException, status

from sqlalchemy import or_, asc, desc, select
from sqlalchemy.orm import Session

from src.tasks.dtos import TaskSchema, AddTagSchema
from src.tasks.models import TaskModel
from src.tags.models import TagModel

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
def get_all_tasks(
    db: Session,
    user: UserModel,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
    tag_id: int | None = None,
):
    query = select(TaskModel).where(TaskModel.user_id == user.id)

    # search --------------
    if search:
        query = query.where(
            or_(
                TaskModel.title.ilike(f"%{search}%"),
                TaskModel.description.ilike(f"%{search}%"),
            )
        )

    # tag id ------------------
    if tag_id:
        query = query.join(TaskModel.tags).where(TagModel.id == tag_id)

    # sorting --------------
    allowed_sort_fields = {
        "id": TaskModel.id,
        "title": TaskModel.title,
        "is_completed": TaskModel.is_completed,
    }

    sort_column = allowed_sort_fields.get(sort_by, TaskModel.id)

    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # pagination ---------------
    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    return db.scalars(query).all()


# ============== get one task ===============================
def get_one_task(task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    return task


# ============== update task ============================
def update_task(body: TaskSchema, task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    body = body.model_dump()

    for field, value in body.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


# ====================== delete task ================================
def delete_task(task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    db.delete(task)
    db.commit()

    return None


# ====================== add tags to task ==========================
def add_tags_to_task(task_id: int, body: AddTagSchema, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task Id {task_id} not found"
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized"
        )

    for tag_id in body.tag_ids:
        tag = db.get(TagModel, tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag Id {tag_id} not found",
            )

        task.tags.append(tag)

    db.commit()
    db.refresh(task)

    return task


# ================ DELETE TAG FROM TASK
def delete_tag_from_task(task_id: int, tag_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found"
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You Are UnAuthorized"
        )

    tag = db.get(TagModel, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found"
        )

    if tag not in task.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not attached to this task",
        )

    task.tags.remove(tag)

    db.commit()

    return None
