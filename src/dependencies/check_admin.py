from fastapi import HTTPException, status, Depends

from src.users.dtos import UserRole
from src.users.models import UserModel
from src.dependencies.is_authenticated import is_authenticated


def admin_required(user: UserModel = Depends(is_authenticated)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return user
