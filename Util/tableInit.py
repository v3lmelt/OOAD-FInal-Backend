from Model import accountModel, dishModel, resultModel, tokenModel, orderModel, orderContentModel
from sqlmodel import SQLModel

from Util.databaseInit import engine

STATIC_FILE_DIRECTORY = r'./img'

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
