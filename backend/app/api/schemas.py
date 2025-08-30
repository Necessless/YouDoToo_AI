from typing import List
import uuid
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from datetime import datetime, timezone


class RegisterUserData(BaseModel):
    email: EmailStr = Field(examples=["example@gmail.com"])
    password: SecretStr = Field(min_length=8, max_length=64, examples=["12345678"])
    name: str = Field(pattern=r"[а-яА-ЯёЕ]+{2,40}")
    last_name: str = Field(pattern=r"[а-яА-ЯёЕ]+{2,40}")

    @field_validator("name")
    @classmethod
    def ensure_name(cls, name: str):
        if len(name.split()) > 1:
            raise ValueError("Name must be a single word")
        return name

    @field_validator("last_name")
    @classmethod
    def ensure_lastname(cls, last_name: str):
        if len(last_name.split()) > 1:
            raise ValueError("Last name must be a single word")
        return last_name


class GetUserData(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: SecretStr
    name: str
    surname: str
    created_at: datetime
    updated_at: datetime | None = None


class LoginData(BaseModel):
    email: EmailStr
    password: SecretStr


class ProfileUpdate(BaseModel):
    name: str | None = Field(pattern=r"[а-яА-ЯёЕ]+{2,40}", default=None)
    last_name: str | None = Field(pattern=r"[а-яА-ЯёЕ]+{2,40}", default=None)

    @field_validator("name")
    @classmethod
    def ensure_name(cls, name: str | None):
        if name is None:
            return name
        if len(name.split()) > 1:
            raise ValueError("Name must be a single word")
        return name

    @field_validator("last_name")
    @classmethod
    def ensure_lastname(cls, last_name: str | None):
        if last_name is None:
            return last_name
        if len(last_name.split()) > 1:
            raise ValueError("Last name must be a single word")
        return last_name


class ConfidentialData(BaseModel):
    new_password: SecretStr | None = Field(
        min_length=8, max_length=64, examples=["12345678"], default=None
    )
    new_email: EmailStr | None = None


class SubTaskPOST(BaseModel):
    name: str = Field(pattern=r"[а-яА-ЯёЕ]+{2,80}", default="Новая задача")
    is_completed: bool = False


class TaskPOST(BaseModel):
    name: str = Field(pattern=r"[а-яА-ЯёЕ]+{2,80}", default="Новая задача")
    description: str | None = Field(max_length=255)
    deadline: datetime | None = None
    is_public: bool = Field(default=True)
    owner_id: uuid.UUID
    subtasks: List[SubTaskPOST] = []

    @field_validator("deadline")
    @classmethod
    def ensure_deadline(cls, deadline: datetime | None):
        if deadline is None:
            return deadline
        deadline = deadline.astimezone(timezone.utc)
        if deadline >= datetime.now(timezone.utc):
            raise ValueError("Deadline must be a date in the future")
        return deadline
    

class TaskPatch(BaseModel):
    id: uuid.UUID
    name: str | None = Field(pattern=r"[а-яА-ЯёЕ]+{2,80}", default=None)
    description: str | None = Field(max_length=255, default=None)
    deadline: datetime | None = None
    is_public: bool | None = Field(default=None)
    is_completed: bool | None = Field(default=None)


class SubTaskPostToMain(BaseModel):
    subtasks: List[SubTaskPOST]
    main_task_id: uuid