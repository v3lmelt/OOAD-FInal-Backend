from typing import Optional

from sqlmodel import SQLModel, Field


class OrderModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_content: str = Field(default="", max_length=2048)

    server_id: Optional[int] = Field(default=None, foreign_key="accountmodel.id")

    start_time: Optional[int] = Field(default=1)
    end_time: Optional[int] = Field(default=-1)

    # 当前状态，0表示还未配餐，1表示正在配餐，2表示配餐完成。
    current_status: Optional[int] = Field(default=0)
    total_price: Optional[float] = Field(default=0.0)
