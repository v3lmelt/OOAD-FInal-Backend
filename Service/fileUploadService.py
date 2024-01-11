# 处理用户上传的文件
import os
import time

from fastapi import APIRouter, UploadFile
from starlette.responses import StreamingResponse

from Model.resultModel import ResultModel, success_result, fail_result
from Util.databaseInit import session_factory
from Util.tableInit import STATIC_FILE_DIRECTORY

router = APIRouter(
    prefix="/api",
    tags=["files"],
)



@router.post("/images", response_model=ResultModel)
async def book_cover_upload(file: UploadFile):
    file.filename = f"book_{time.time()}.jpg"
    # 保存地址
    save_path = STATIC_FILE_DIRECTORY
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    with open(os.path.join(save_path, file.filename), 'wb') as f:
        data = await file.read()
        f.write(data)

    return success_result({"filename": file.filename})


# 根据文件id进行图像的获取
@router.get("/images/{file_name}")
async def get_book_cover_by_ID(file_name: str):
    with session_factory() as session:
        try:
            path = os.path.join(STATIC_FILE_DIRECTORY, file_name)
            if not os.path.exists(path):
                return fail_result("img file didn't exist!")
            image_file = open(os.path.join(STATIC_FILE_DIRECTORY, file_name), mode='rb')
            return StreamingResponse(image_file, media_type="image/jpg")
        except Exception as e:
            return fail_result(str(e))



