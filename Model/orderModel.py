from typing import Optional

from sqlmodel import SQLModel, Field


class OrderModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_content: str = Field(default="", max_length=2048)

    server_id: Optional[int]

