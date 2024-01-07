from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class accountOut(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default=None, max_length=12, nullable=False)


class account(accountOut, table=True):
    password: str = Field(default=None, max_length=256, nullable=False)
    bind_id: str = Field(default=None, max_length=20, nullable=False)
    email: str = Field(default=None, max_length=20, nullable=False)
    role: Optional[str] = Field(default="user", max_length=10)
    book_borrow_available: Optional[int] = Field(default=3)


class accountOutAdmin(SQLModel):
    id: int
    username: str
    bind_id: str
    email: str
    role: str
    book_borrow_available: int
