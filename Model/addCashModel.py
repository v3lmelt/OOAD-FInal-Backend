from sqlmodel import SQLModel


class AddCashModel(SQLModel):
    user_id: int
    cash_to_add: int
