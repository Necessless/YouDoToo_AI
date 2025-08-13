from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData, DateTime, func, ForeignKey
from .config import settings
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """Базовый абстрактный класс для всех моделей"""

    __abstract__ = True

    metadata = MetaData(naming_convention=settings.database.naming_convention)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class Task(Base):
    """Класс задач, с дедлайном и флагом на публичность"""

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    deadline: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    is_public: Mapped[bool] = mapped_column(default=True)

    owner: Mapped["User"] = relationship(back_populates="tasks")
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )


class User(Base):
    """Класс пользователя"""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()

    tasks: Mapped[List["Task"]] = relationship(back_populates="owner")
