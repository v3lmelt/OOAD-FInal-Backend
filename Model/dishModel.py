from typing import Optional

from sqlmodel import SQLModel, Field


class DishTypeModel(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=50)

class DishModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="菜品", max_length=50)
    price: float = Field(default=0.0)
    dish_type: int = Field(foreign_key="dishtypemodel.id")



