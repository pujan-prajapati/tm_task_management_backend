from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base
from src.utils.associations import task_tags

if TYPE_CHECKING:
    from src.tasks.models import TaskModel


class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tasks: Mapped[list["TaskModel"]] = relationship(
        secondary=task_tags, back_populates="tags"
    )
