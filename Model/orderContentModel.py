from sqlmodel import SQLModel


# 前端提交的订单内容
class OrderContentModel(SQLModel):
    dish_type: int
    id: int
    price: float
    quantity: int

    def serializeOrderContent(self):
        return {"dish_type": self.dish_type,
                "id": self.id,
                "price": self.price,
                "quantity": self.quantity}
