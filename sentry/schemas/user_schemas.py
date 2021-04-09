from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """ Проверяет sign-up запрос """
    email: EmailStr
    name: str
    password: str


class UserAuth(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    username: EmailStr
    password: str


class UserBase(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    id: int
    email: EmailStr
    name: str


class TokenBase(BaseModel):
    id: int
    email: EmailStr
    name: str
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


class User(UserBase):
    """ Формирует тело ответа с деталями пользователя и токеном """
    token: TokenBase = dict()


class UserProfile(UserAuth):
    createdAt: datetime
    updatedAt: datetime
    bio: str
    image: str
    token: str