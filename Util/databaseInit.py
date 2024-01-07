from sqlmodel import create_engine, Session

MYSQL_URL = 'mysql+mysqldb://root:w1ldflow3r@localhost:3306/OOAD?charset=utf8mb4'

engine = create_engine(MYSQL_URL, echo=True)


def session_factory():
    return Session(engine)
