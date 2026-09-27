from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.tags.models import TagModel

from src.utils.db import Base
from src.utils.associations import task_tags


class TaskModel(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id", ondelete="CASCADE")
    )

    tags: Mapped[list["TagModel"]] = relationship(
        secondary=task_tags, back_populates="tasks"
    )
