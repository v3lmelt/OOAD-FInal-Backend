from typing import Any

from sqlmodel import SQLModel


# 前端提交的订单内容
def deserializeOrderContent(dic):
    return OrderContentModel(dish_type=dic.dish_type,
                             id=dic.id,
                             price=dic.price,
                             quantity=dic.quantity)


class OrderContentModel(SQLModel):
    dish_type: int
    id: int
    price: float
    quantity: int

    def __init__(self, **data: Any):
        super().__init__(**data)

    def serializeOrderContent(self):
        return {"dish_type": self.dish_type,
                "id": self.id,
                "price": self.price,
                "quantity": self.quantity}
