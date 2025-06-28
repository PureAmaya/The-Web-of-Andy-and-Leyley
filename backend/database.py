# 文件: backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from backend.core.config import get_settings

settings = get_settings()

# 异步引擎和会话工厂的定义
async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)

# AsyncSessionLocal 是一个会话“模板”，我们可以用它来创建新的会话实例
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# get_async_session 函数现在专为 FastAPI 的依赖注入系统服务
# 它不应在 admin_auth.py 中被直接调用
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# --- 同步引擎部分保持不变 ---
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=True)

def create_db_and_tables_sync():
    SQLModel.metadata.create_all(sync_engine)