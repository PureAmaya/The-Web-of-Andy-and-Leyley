# database.py
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DATABASE_FILE_PATH = Path(__file__).parent / "portal_app.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE_PATH.resolve()}"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


# 3. 创建一个函数，用于在应用启动时创建所有定义的数据库表
def create_db_and_tables():
    """
    创建数据库文件（如果不存在）以及所有在 SQLModel 中定义的表。
    """
    # SQLModel.metadata.create_all() 会检查所有继承自 SQLModel 的类，
    # 并在数据库中创建相应的表（如果表尚不存在）。
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session