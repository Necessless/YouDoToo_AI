from pydantic import BaseModel, EmailStr, Field, SecretStr
from datetime import datetime


class RegisterUserData(BaseModel):
    email: EmailStr = Field(examples=['example@gmail.com'])
    password: SecretStr = Field(min_length=8, max_length=64, examples=['12345678'])
    name: str = Field()
    surname: str = Field()
    created_at: datetime = Field(default=datetime.now())


class GetUserData(BaseModel):
    email: EmailStr
    password: SecretStr
    name: str
    surname: str
    created_at: datetime
    updated_at: datetime | None = None
