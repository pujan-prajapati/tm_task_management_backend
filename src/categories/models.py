from typing import TYPE_CHECKING, List

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.db import Base

if TYPE_CHECKING:
    from src.tasks.models import TaskModel


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False
    )

    tasks: Mapped[List["TaskModel"]] = relationship(back_populates="category")

    __table_args__ = (UniqueConstraint("user_id", "name"),)
