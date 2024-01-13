import os

from fastapi import APIRouter
from fastapi_pagination import paginate, Page
from sqlmodel import select

from Model.dishModel import DishModel, DishQueryModel
from Model.resultModel import success_result, fail_result
from Util.databaseInit import session_factory
from Util.tableInit import STATIC_FILE_DIRECTORY

router = APIRouter(
    prefix="/api/dish",
    tags=["dish"],
)


# 根据id获取菜品信息
@router.get("/get-dish/{id}")
async def get_dish_by_id(id: int):
    with session_factory() as session:
        try:
            data = session.get(DishModel, id)
            return success_result(data)
        except Exception as e:
            return fail_result(str(e))


# 获取所有菜品
@router.get("/get-all-dish")
async def get_all_dish() -> Page[DishModel]:
    with session_factory() as session:
        return paginate(session.query(DishModel).all())


# 删除指定菜品
@router.delete("/delete-dish/{id}")
async def delete_dish_by_id(id: int):
    with session_factory() as session:
        try:
            data = session.get(DishModel, id)
            # 检查对应的菜品图片是否存在
            cover_path = os.path.join(STATIC_FILE_DIRECTORY, data.image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

            session.delete(data)
            session.commit()
        except Exception as e:
            return fail_result(str(e))
        return success_result(None)


# 添加指定菜品，修改指定菜品也是在这里！
@router.post("/add-dish")
async def add_dish(dish_to_add: DishModel):
    with session_factory() as session:
        try:
            # 检查是否已存在菜品
            if dish_to_add.id is not None:
                db_obj = session.get(DishModel, dish_to_add.id)
                if db_obj is not None:
                    db_obj.name = dish_to_add.name
                    db_obj.dish_type = dish_to_add.dish_type
                    db_obj.price = dish_to_add.price
                    db_obj.image = dish_to_add.image
                    db_obj.ingredients = dish_to_add.ingredients
                    session.add(db_obj)
            else:
                session.add(dish_to_add)
            session.commit()
        except Exception as e:
            return fail_result(str(e))
    return success_result(None)


# 模糊查找指定的菜品
@router.post("/find-dish")
async def find_dish(dish_to_find: DishQueryModel) -> Page[DishModel]:
    with session_factory() as session:
        try:
            query = select(DishModel)
            if dish_to_find.id is not None:
                query = query.where(DishModel.id.like(f"%{dish_to_find.id}%"))
            if dish_to_find.name is not None:
                query = query.where(DishModel.name.like(f"%{dish_to_find.name}%"))
            if dish_to_find.dish_type is not None:
                query = query.where(DishModel.dish_type.like(f"%{dish_to_find.dish_type}%"))
            result = session.exec(query).all()
        except Exception as e:
            return fail_result(str(e))
    return paginate(result)
