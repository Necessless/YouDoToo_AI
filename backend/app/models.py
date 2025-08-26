from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData, DateTime, func, ForeignKey
from config import settings
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
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class SubTask(Base):
    """Подзадачи для основных задач"""
    __tablename__ = "subtasks"

    name: Mapped[str] = mapped_column()
    is_completed: Mapped[bool] = mapped_column(default=False)

    parent: Mapped["Task"] = relationship(back_populates="subtasks")
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE")
    )


class Task(Base):
    """Класс задач с дедлайном и флагом на публичность"""

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = None
    deadline: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    is_public: Mapped[bool] = mapped_column(default=True)

    owner: Mapped["User"] = relationship(back_populates="tasks")
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    is_completed: Mapped[bool] = mapped_column(default=False)

    subtasks: Mapped[List["SubTask"]] = relationship(back_populates="parent")


class User(Base):
    """Класс пользователя"""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()

    tasks: Mapped[List["Task"]] = relationship(back_populates="owner")
