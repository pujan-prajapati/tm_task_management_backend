from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base

from src.utils.associations import task_assignment

if TYPE_CHECKING:
    from src.tasks.models import TaskModel


class UserModel(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone: Mapped[str] = mapped_column(String, unique=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    assigned_tasks: Mapped[list["TaskModel"]] = relationship(
        secondary=task_assignment, back_populates="assigned_users"
    )
