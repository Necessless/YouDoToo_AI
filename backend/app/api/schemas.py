import uuid
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from datetime import datetime


class RegisterUserData(BaseModel):
    email: EmailStr = Field(examples=['example@gmail.com'])
    password: SecretStr = Field(min_length=8, max_length=64, examples=['12345678'])
    name: str = Field(pattern=r"^[A-Za-z]{2,14}$")
    last_name: str = Field(pattern=r"^[A-Za-z]{2,30}$")

    @field_validator('name')
    @classmethod
    def ensure_name(cls, name: str):
        if (len(name.split()) > 1):
            raise ValueError('Name must be a single word')
        return name

    @field_validator('last_name')
    @classmethod
    def ensure_lastname(cls, last_name: str):
        if (len(last_name.split()) > 1):
            raise ValueError('Last name must be a single word')
        return last_name


class GetUserData(BaseModel):
    id: uuid.UUID
    email: EmailStr
    password: SecretStr
    name: str
    surname: str
    created_at: datetime
    updated_at: datetime | None = None
