from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


# 菜品类型表
class DishTypeModel(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=50)


# 菜品表
class DishModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="菜品", max_length=50)
    price: float = Field(default=0.0)
    image: str = Field(max_length=512)
    ingredients: str = Field(max_length=512)
    # 注意，菜品类型是int类型！
    dish_type: int = Field(foreign_key="dishtypemodel.id")
    count: int = Field(default=0)


# 菜品查询数据验证
class DishQueryModel(BaseModel):
    id: Optional[int]
    name: Optional[str]

    # 注意，菜品类型是int类型！
    dish_type: Optional[int]
