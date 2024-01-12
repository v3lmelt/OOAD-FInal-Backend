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
        user_in_db = session.get(AccountModel, add_cash_info.user_id)
        if user_in_db is None:
            return fail_result("该用户不存在!")
        user_in_db.cash += add_cash_info.cash_to_add
        session.commit()
    return success_result("操作成功!")
