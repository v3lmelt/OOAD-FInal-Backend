import pandas as pd
from fastapi import APIRouter, Depends
from sqlmodel import col

from Model.accountModel import AccountModel
from Model.orderModel import OrderModel
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
        df = sqlmodel_to_df(orders)
        df["end_time"] = pd.to_datetime(df["end_time"], unit='s')
        df.set_index('end_time', inplace=True)

        df["sumed"] = 1
        hourly_data = df.resample('H').sum().head()
        print(hourly_data)

        objs = df_to_sqlmodel(hourly_data)
        return objs

