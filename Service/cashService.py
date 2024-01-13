from fastapi import APIRouter, Depends

from Model.accountModel import AccountModel
from Model.addCashModel import AddCashModel
from Model.resultModel import fail_result, success_result
from Service.accountService import get_current_user
from Util.databaseInit import session_factory

router = APIRouter(
    prefix="/api/cash",
    tags=["cash"],
)


# 注，此接口仅示意性质，未与第三方支付平台链接。
@router.post("/add")
async def add_cash(add_cash_info: AddCashModel, user: AccountModel = Depends(get_current_user)):
    with session_factory() as session:
        user.cash += add_cash_info.cash_to_add
        session.commit()
    return success_result("操作成功!")


@router.get("/get-cash")
async def get_cash(user: AccountModel = Depends(get_current_user)):
    with session_factory() as session:
        try:
            return success_result(user.cash)
        except Exception as e:
            return fail_result(str(e))
