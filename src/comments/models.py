from src.core.db import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("user_tasks.id", ondelete="CASCADE"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False
    )
