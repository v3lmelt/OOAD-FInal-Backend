from datetime import timedelta, datetime
from enum import Enum
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import Page, paginate
from jose import jwt, JWTError
from passlib.context import CryptContext

from sqlmodel import select
from starlette import status

from Model.accountModel import AccountModel, AccountOut, AccountOutAdmin
from Model.resultModel import fail_result, success_result
from Model.tokenModel import Token, TokenData
from Util.databaseInit import session_factory

router = APIRouter(
    prefix="/api/account",
    tags=["account"],
)


# 所有可能的权限类型
class role_types(Enum):
    USER = 1
    ADMIN = 2
    STAFF = 3


# Token过期的时间，这里定义为10天
ACCESS_TOKEN_EXPIRES_IN_MINUTES = 60 * 24 * 10
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/account/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "2023_OOAD_FINAL_ASSIGNMENT"
ALGORITHM = "HS256"


# 创建访问Token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"expire": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# 获取哈希过后的密码
def get_hashed_password(password: str):
    return pwd_context.hash(password)


# 验证用户名与密码是否匹配
def auth_user(username, plain_password):
    with session_factory() as session:
        try:
            # 尝试通过用户名查找对应用户(唯一的)
            result: AccountModel = get_user_by_name(username)
            if result is not None:
                if pwd_context.verify(plain_password, result.password):
                    return result
            return None
        except Exception as e:
            return None


# 通过用户名获取用户
def get_user_by_name(username: str):
    with session_factory() as session:
        stmt = select(AccountModel).where(AccountModel.username == username)
        result = session.exec(stmt)

        return result.first()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    user: AccountModel = get_user_by_name(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# 判断当前用户是否是管理员
def get_current_admin(user: AccountModel = Depends(get_current_user)):
    permission_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permission denied",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user.role != "admin":
        raise permission_exception
    else:
        return user


# 判断当前用户是否是指定的权限类型
def check_user_permission(permission_type: role_types, user: AccountModel = Depends(get_current_user)):
    permission_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permission denied",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user.role != permission_type.name:
        raise permission_exception
    else:
        return user


@router.get("/test-check-permission")
async def check_user_permission_test(permission_type: role_types):
    return check_user_permission(permission_type)


# 创建Token
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 注意，密码在数据库中并不是明文存储的！
    user: AccountModel = auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "role": user.role},
                                       expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register_account(submit_account: AccountModel):
    with session_factory() as session:
        try:
            # 先查询是否已经存在此用户名
            user_in_db = get_user_by_name(submit_account.username)
            if user_in_db is not None:
                return fail_result("User with same username already exist!")

            # 再查询是否存在邮箱
            stmt = select(AccountModel).where(AccountModel.email == submit_account.email)
            user_in_db = session.exec(stmt)

            if user_in_db.first() is not None:
                return fail_result("User with same email already exist!")

            # 注意密码不能明文存储，因此需要先加密
            submit_account.password = get_hashed_password(submit_account.password)
            session.add(submit_account)
            session.commit()
            return success_result("Successfully add account!")
        except Exception as e:
            return fail_result(str(e))


# 获取自身
@router.get("/me", response_model=AccountOut)
async def read_user_me(current_account: AccountOut = Depends(get_current_user)):
    return current_account


# 查询所有用户，要求管理员权限
@router.get("/get-all")
async def get_all_user(current_account=Depends(get_current_admin)) -> Page[AccountOutAdmin]:
    with session_factory() as session:
        stmt = select(AccountModel)
        user_in_db = session.exec(stmt).all()
        return paginate(user_in_db)


# 修改指定用户，要求管理员权限
@router.post("/modify-user")
async def modify_user(user_to_modify: AccountOutAdmin, current_account=Depends(get_current_admin)):
    with session_factory() as session:
        # 由于是修改，那么ID一定存在
        user_in_db = session.get(AccountModel, user_to_modify.id)
        if user_in_db is None:
            return fail_result("该用户不存在于数据库中!")
        user_in_db.cash = user_to_modify.cash
        user_in_db.username = user_to_modify.username
        user_in_db.role = user_to_modify.role
        user_in_db.email = user_to_modify.email

        session.add(user_in_db)
        session.commit()
        return success_result("操作成功!")


# 删除指定用户，要求管理员权限
@router.get("/delete-user")
async def delete_user(userId: int, current_account=Depends(get_current_admin)):
    with session_factory() as session:
        # 查询指定用户
        user_in_db = session.get(AccountModel, userId)
        if user_in_db is None:
            return fail_result("该用户不存在于数据库中!")

        session.delete(user_in_db)
        session.commit()
        return success_result("操作成功!")
