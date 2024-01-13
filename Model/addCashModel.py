from sqlmodel import SQLModel


class AddCashModel(SQLModel):
    cash_to_add: int
