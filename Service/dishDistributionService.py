import json
import pickle
import time
from datetime import date

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlmodel import select, or_, and_

from Model.accountModel import AccountModel
from Model.dishModel import DishModel
from Model.orderContentModel import OrderContentModel
from Model.orderModel import OrderModel
from Model.orderStatusModifyModel import OrderStatusModifyModel
from Model.resultModel import fail_result, success_result
from Service.accountService import get_current_user
from Util.databaseInit import session_factory

router = APIRouter(
    prefix="/api/dish-distribution",
    tags=["dish-distribution"],
)


@router.post("/submit-order")
async def submit_order(order_content: list[OrderContentModel], seat_id: int, user: AccountModel = Depends(get_current_user)):
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

                # 对应菜品的受欢迎程度 + 点的份数
                dish_obj.count -= item.quantity
                dish_obj.popularity += item.quantity

                session.add(dish_obj)
            # 创建后台订单
            print(order_content)

            # 序列化订单内容
            # dish_type: int
            # id: int
            # price: float
            # quantity: int

            json_order_content = json.dumps(order_content, default=OrderContentModel.serializeOrderContent)
            order_obj = OrderModel(order_content=json_order_content, start_time=time.time(), total_price=total_price, seat_id=seat_id,
                                   order_user_id=user.id)

            session.add(order_obj)
            session.commit()
        except Exception as e:
            return fail_result(str(e))
        return success_result("订单成功创建!")


@router.get("/get-order/{id}")
async def get_order_by_id(id: int, user: AccountModel = Depends(get_current_user)):
    with session_factory() as session:
        order = session.get(OrderModel, id)
        if order is None:
            return fail_result("该订单不存在!")
        return success_result(order)

# 获取所有订单内容，供员工使用
@router.get("/get-order-staff")
async def get_order_staff(user: AccountModel = Depends(get_current_user)) -> Page[OrderModel]:
    with session_factory() as session:
        stmt = select(OrderModel).where(and_(OrderModel.current_status != 2, or_(OrderModel.server_id is None, OrderModel.server_id == user.id)))
        order_in_db = session.exec(stmt).all()
        return paginate(order_in_db)

# 获取所有订单内容，供用户使用
@router.get("/get-order")
async def get_order(user: AccountModel = Depends(get_current_user)) -> Page[OrderModel]:
    with session_factory() as session:
        stmt = select(OrderModel).where(OrderModel.order_user_id == user.id)
        order_in_db = session.exec(stmt).all()
        return paginate(order_in_db)


# 开始配餐，current_status表示当前状态，0表示还未配餐，1表示正在配餐，2表示配餐完成。
@router.post("/modify-distribution-status")
async def modify_distribution_status(order_to_modify: OrderStatusModifyModel, user: AccountModel = Depends(get_current_user)):
    with session_factory() as session:
        try:
            orderContent = session.get(OrderModel, order_to_modify.orderID)
            if orderContent is None:
                return fail_result("修改订单状态失败!")
            orderContent.current_status = order_to_modify.orderNewStatus

            # 如果刚刚开始配送，则登记工作人员
            if (orderContent.server_id is None or orderContent.server_id == -1) and order_to_modify.orderNewStatus == 1:
                orderContent.server_id = user.id

            if order_to_modify.orderNewStatus == 2:
                if user.id == orderContent.server_id:
                    # 订单完成
                    orderContent.end_time = time.time()
                else:
                    return fail_result("工作人员不一致!")

            session.add(orderContent)
            session.commit()
        except Exception as e:
            return fail_result(str(e))
    return success_result("修改订单状态成功!")