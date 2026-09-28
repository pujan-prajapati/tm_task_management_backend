from sqlalchemy import Table, Column, ForeignKey
from src.core.db import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id", ForeignKey("user_tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
