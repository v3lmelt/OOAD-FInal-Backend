from sqlmodel import SQLModel


class OrderStatusModifyModel(SQLModel):
    orderID: int
    orderNewStatus: int