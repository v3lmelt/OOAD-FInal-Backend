import typing
from typing import Union

from pydantic import BaseModel


class ResultModel(BaseModel):
    code: int
    message: Union[str, None]
    data: Union[typing.Any, None]

    class Config:
        orm_mode = True


class Result:
    def __init__(self, code: int, message: str, data: typing.Any):
        self.code = code
        self.message = message
        self.data = data


def success_result(data: typing.Any):
    return Result(200, "Operation Succeed!", data)


def fail_result(message: str):
    return Result(-1, message, None)
