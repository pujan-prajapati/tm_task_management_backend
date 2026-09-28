from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from src.core.db import Base


class UserModel(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone: Mapped[str] = mapped_column(String, unique=True)

    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
