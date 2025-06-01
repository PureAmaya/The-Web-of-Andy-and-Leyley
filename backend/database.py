# backend/database.py
from sqlmodel import SQLModel, create_engine, Session # <--- 确保这里的 Session 是从 sqlmodel 导入的
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from backend.core.config import settings
from sqlalchemy.orm import sessionmaker # 这个可以保留给异步会话工厂使用

# --- 异步引擎和会话 ---
async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)

async def get_async_session() -> AsyncSession:
    async_session_factory = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        # ... (异步会话逻辑保持不变) ...
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- 同步引擎 (主要用于 create_tables.py 或 Alembic 迁移) ---
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=True)

def create_db_and_tables_sync():
    SQLModel.metadata.create_all(sync_engine)

# --- 修改 get_session 函数 ---
def get_session(): # 这个同步的 get_session 给 FastAPI 的同步端点或同步脚本用
    # 直接使用 SQLModel 的 Session 上下文管理器
    with Session(sync_engine) as session: # <--- 使用从 sqlmodel 导入的 Session
        # print(f"DEBUG: Type of session created in get_session: {type(session)}") # 用于调试
        try:
            yield session
            # 通常在依赖项中不自动提交，让路径操作函数自己控制事务
            # session.commit()
        except Exception:
            session.rollback()
            raise
        # finally: # SQLModel 的 Session 上下文管理器会自动处理关闭
            # session.close()