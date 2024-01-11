import json
import pickle

from fastapi import APIRouter, Depends

from Model.accountModel import AccountModel
from Model.dishModel import DishModel
from Model.orderContentModel import OrderContentModel
from Model.orderModel import OrderModel
from Model.resultModel import fail_result, success_result
from Service.accountService import get_current_user
from Util.databaseInit import session_factory

router = APIRouter(
    prefix="/api/dish-distribution",
    tags=["dish-distribution"],
)


@router.post("/submit-order")
async def get_order(order_content: list[OrderContentModel], user: AccountModel = Depends(get_current_user)):
    total_price = 0.0
    # 计算商品总价
    for item in order_content:
        total_price += item.price * item.quantity
    # 检查对应用户余额是否足够
    if user.cash < total_price:
        return fail_result("余额不足!")
    with session_factory() as session:
        try:
            user.cash -= total_price
            session.add(user)

            # with session_factory() as session:
            #     user_obj = session.get(AccountModel, user.id)
            #     user_obj.cash -= total_price
            #     session.add(user_obj)

            # 扣除对应菜品数量
            for item in order_content:
                dish_id = item.id
                dish_obj = session.get(DishModel, dish_id)

                if dish_obj is None:
                    return fail_result("该菜品不存在!")
                if dish_obj.count < item.quantity:
                    return fail_result("该菜品存量不足!")

                dish_obj.count -= item.quantity
                session.add(dish_obj)
            # 创建后台订单
            print(order_content)

            # 序列化订单内容
            # dish_type: int
            # id: int
            # price: float
            # quantity: int

            json_order_content = json.dumps(order_content, default=OrderContentModel.serializeOrderContent)

            order_obj = OrderModel(order_content=json_order_content)
            session.add(order_obj)
            session.commit()
        except Exception as e:
            return fail_result(str(e))
        return success_result("订单成功创建!")
