import math

from fastapi import HTTPException, status

from sqlalchemy import or_, asc, desc, select, func
from sqlalchemy.orm import Session, selectinload

from src.users.models import UserModel
from src.tags.models import TagModel
from src.categories.models import CategoryModel

from src.tasks.models import TaskModel
from src.tasks.dtos import TaskSchema, AddTagSchema, TaskStatus, TaskPriority

from src.utils.helpers import success_response


# =========== CREATE TASK =======================
def create_task(body: TaskSchema, db: Session, user: UserModel):

    if body.category_id is not None:
        category = db.get(CategoryModel, body.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category Id {body.category_id} not found",
            )

        if category.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to use this category",
            )

    new_task = TaskModel(
        title=body.title,
        description=body.description,
        priority=body.priority,
        status=body.status,
        user_id=user.id,
        category_id=body.category_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return success_response(data=new_task, message="Task Created Successfully")


# ============== GET ALL TASKS =============================
def get_all_tasks(
    db: Session,
    user: UserModel,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
    tag_ids: list[int] | None = None,
    priority: TaskPriority | None = None,
    status: TaskStatus | None = None,
    category_id: int | None = None,
):
    query = (
        select(TaskModel)
        .options(selectinload(TaskModel.tags))
        .where(TaskModel.user_id == user.id)
    )

    # search --------------
    if search:
        query = query.where(
            or_(
                TaskModel.title.ilike(f"%{search}%"),
                TaskModel.description.ilike(f"%{search}%"),
            )
        )

    # status --------------
    if status:
        query = query.where(TaskModel.status == status)

    # priority --------------
    if priority:
        query = query.where(TaskModel.priority == priority)

    # category id --------------
    if category_id:
        query = query.where(TaskModel.category_id == category_id)

    # tag id ------------------
    if tag_ids:
        query = (
            query.join(TaskModel.tags)
            .where(TagModel.id.in_(tag_ids))
            .group_by(TaskModel.id)
            .having(func.count(TagModel.id) == len(tag_ids))
        )

    # total tasks
    total = db.scalar(select(func.count()).select_from(query.subquery()))

    # sorting and ordering --------------
    allowed_sort_fields = {
        "id": TaskModel.id,
        "title": TaskModel.title,
        "priority": TaskModel.priority,
        "status": TaskModel.status,
    }

    sort_column = allowed_sort_fields.get(sort_by, TaskModel.id)

    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # pagination ---------------
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    tasks = db.scalars(query).all()

    # Total pages -----------------
    total_pages = math.ceil(total / limit)

    return success_response(
        data={
            "items": tasks,
            "page": page,
            "limit": limit,
            "total": total,
            "total_page": total_pages,
        },
        message="All Task Fetched Successfully",
    )


# ============== GET ONE TASK ===============================
def get_one_task(task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )

    return success_response(data=task, message="Task Fetched Successfully")


# ============== UPDATE TASK ============================
def update_task(body: TaskSchema, task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )

    if body.category_id is not None:
        category = db.get(CategoryModel, body.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category Id {body.category_id} not found",
            )

        if category.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to use this category",
            )

    task.title = body.title
    task.description = body.description
    task.priority = body.priority
    task.status = body.status
    task.category_id = body.category_id

    db.commit()
    db.refresh(task)

    return success_response(data=task, message="Task Updated Successfully")


# ====================== DELETE TASK ================================
def delete_task(task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(404, detail=f"Task Id {task_id} not found")

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )

    db.delete(task)
    db.commit()

    return success_response(data=None, message="Task Deleted Successfully")


# ====================== ADD TAGS TO TASK ==========================
def add_tags_to_task(task_id: int, body: AddTagSchema, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task Id {task_id} not found"
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
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

    return success_response(data=task, message="Tag Added To Task Successfully")


# ================ DELETE TAG FROM TASK ================================
def delete_tag_from_task(task_id: int, tag_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found"
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You Are UnAuthorized"
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

    return success_response(data=None, message="Tag Removed from Task")
