import sqlmodel
from databaseInit import engine

STATIC_FILE_DIRECTORY = r'./img'

if __name__ == "__main__":
    sqlmodel.metadata.create_all(engine)
