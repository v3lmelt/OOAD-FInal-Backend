import pandas as pd
from fastapi import APIRouter, Depends
from sqlmodel import col, select

from Model.accountModel import AccountModel
from Model.orderModel import OrderModel
from Model.resultModel import success_result, fail_result
from Service.accountService import get_current_admin
from Util.databaseInit import session_factory
from Util.pandasUtil import sqlmodel_to_df, df_to_sqlmodel

router = APIRouter(
    prefix="/api/statistic",
    tags=["cash"],
)


# 用餐人数统计
@router.get("/diner-statistic")
async def get_diners(user: AccountModel = Depends(get_current_admin)):
    with session_factory() as session:
        orders = session.query(OrderModel).all()

        if orders is None or len(orders) == 0:
            return fail_result("当前尚未有订单记录!")

        df = sqlmodel_to_df(orders)
        df["end_time"] = pd.to_datetime(df["end_time"], unit='s')
        df.set_index('end_time', inplace=True)

        df["sumed"] = 1
        hourly_data = df.resample('H').sum().head()
        print(hourly_data)

        objs = df_to_sqlmodel(hourly_data)
        return success_result(objs)


@router.get("/average-time")
async def get_average_time(user: AccountModel = Depends(get_current_admin)):
    with session_factory() as session:
        try:
            orders = session.query(OrderModel).all()
            total = len(orders)
            sum = 0
            for item in orders:
                sum += (item.end_time - item.start_time)
            return success_result(sum / total)
        except Exception as e:
            return fail_result(str(e))


@router.get("/get-workload/{id}")
async def get_workload(id: int, user: AccountModel = Depends(get_current_admin)):
    with session_factory() as session:
        try:
            work = session.exec(select(OrderModel).where(OrderModel.server_id == id)).all()
            if work is None or len(work) == 0:
                return fail_result("该工作人员尚未有服务订单!")

            return success_result(len(work))
        except Exception as e:
            return fail_result(str(e))


@router.get("/get-income/{id}")
async def get_income(id: int, user: AccountModel = Depends(get_current_admin)):
    with session_factory() as session:
        try:
            total_income = 0
            work = session.exec(select(OrderModel).where(OrderModel.server_id == id)).all()
            if work is None or len(work) == 0:
                return fail_result("该工作人员尚未有服务订单!")
            for item in work:
                total_income += item.total_price
            return success_result(total_income)
        except Exception as e:
            return fail_result(str(e))
