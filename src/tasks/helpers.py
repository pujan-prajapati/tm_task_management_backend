from fastapi import HTTPException, status

from src.users.models import UserModel
from src.tasks.models import TaskModel


def check_task_access(task: TaskModel, user: UserModel):
    if task.user_id == user.id:
        return

    if user in task.assigned_users:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You Are Not Authorized To Access This Task",
    )
