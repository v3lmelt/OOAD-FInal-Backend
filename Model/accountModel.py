from typing import Optional
from sqlmodel import SQLModel, Field


class AccountOut(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default=None, max_length=12, nullable=False)


class AccountModel(AccountOut, table=True):
    password: str = Field(default=None, max_length=256, nullable=False)
    bind_id: str = Field(default=None, max_length=20, nullable=False)
    email: str = Field(default=None, max_length=20, nullable=False)
    role: Optional[str] = Field(default="user", max_length=10)
    cash: Optional[float] = Field(default=0)


class AccountOutAdmin(SQLModel):
    id: int
    username: str
    bind_id: str
    email: str
    role: str
    cash: float
