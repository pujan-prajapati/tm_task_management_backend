from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.comments.dtos import CommentSchema
from src.comments.models import CommentModel
from src.users.models import UserModel
from src.tasks.models import TaskModel

from src.notifications.controllers import create_notification
from src.utils.helpers import success_response
from src.tasks.helpers import check_task_access
from src.utils.mail import send_email

from src.websocket.manager import manager

from src.jobs.queue import email_queue, email_retry
from src.jobs.email_jobs import send_email_job


# =================== CREATE COMMENT =========================
async def create_comment(
    body: CommentSchema,
    task_id: int,
    db: Session,
    user: UserModel,
):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    check_task_access(task, user)

    new_comment = CommentModel(content=body.content, task_id=task_id, user_id=user.id)

    db.add(new_comment)

    # Collect everyone who should receive the notification
    recipients = set()

    # Add Task owner
    if task.user_id != user.id:
        recipients.add(task.user_id)

    # Add Assigned users
    for assigned_user in task.assigned_users:
        if assigned_user.id != user.id:
            recipients.add(assigned_user.id)

    # create database notifications + email notifications
    for recipent_id in recipients:
        recipient = db.get(UserModel, recipent_id)

        create_notification(
            message=f"New comment on task: {task.title}", user_id=recipent_id, db=db
        )

        await manager.send_to_user(
            user_id=recipent_id,
            message={
                "type": "comment_added",
                "message": f"New comment on task: {task.title}",
                "task_id": task.id,
            },
        )

        # Email notification
        email_queue.enqueue(
            send_email_job,
            emails=[recipient.email],
            subject="New Comment On Your Task",
            html=f"""
                    <h2>New Comment</h2>
                    <p>Hi {recipient.name},</p>
                    <p><strong>{task.title}</strong></p>
                    <p><strong>Comment:</strong></p>
                    <p>{new_comment.content}</p>
                    <p>Please login to TaskMaster to view the task.</p>
                """,
            retry=email_retry,
        )
        # backgroud_tasks.add_task(
        #     send_email,
        #     emails=[recipient.email],
        #     subject="New Comment On Your Task",
        #     html=f"""
        #         <h2>New Comment</h2>
        #         <p>Hi {recipient.name},</p>
        #         <p><strong>{task.title}</strong></p>
        #         <p><strong>Comment:</strong></p>
        #         <p>{new_comment.content}</p>
        #         <p>Please login to TaskMaster to view the task.</p>
        #     """,
        # )

    db.commit()
    db.refresh(new_comment)

    return success_response(data=new_comment, message="Comment Created Successfully")


# ================ GET TASK COMMENTS ============================
def get_task_comments(task_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found"
        )

    check_task_access(task, user)

    query = (
        select(CommentModel)
        .where(CommentModel.task_id == task_id)
        .order_by(CommentModel.id.asc())
    )
    comments = db.scalars(query).all()

    return success_response(data=comments, message="Comments Fetched Successfully")


# ================ UPDATE COMMENTS ============================
def update_comment(
    task_id: int, comment_id: int, body: CommentSchema, db: Session, user: UserModel
):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tas Not Found"
        )

    check_task_access(task, user)

    comment = db.get(CommentModel, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Comment Not Found"
        )

    if comment.task_id != task.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment Does Not Belog To This Task",
        )

    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You Can Only Update Your Own Comment",
        )

    comment.content = body.content

    db.commit()
    db.refresh(comment)

    return success_response(data=comment, message="Comment Updated Successfully")


# ================ DELETE COMMENTS ============================
def delete_comment(task_id: int, comment_id: int, db: Session, user: UserModel):
    task = db.get(TaskModel, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tas Not Found"
        )

    check_task_access(task, user)

    comment = db.get(CommentModel, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Comment Not Found"
        )

    if comment.task_id != task.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment Does Not Belog To This Task",
        )

    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You Can Only Delete Your Own Comment",
        )

    db.delete(comment)
    db.commit()

    return success_response(data=None, message="Comment Deleted Successfully")
