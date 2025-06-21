# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- 新增部分开始 ---
# 解决 Alembic 无法找到模块的问题
import sys
from pathlib import Path
# 将项目根目录添加到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.core.config import settings # 导入您的 settings
from backend.models import SQLModel # 导入 SQLModel 基类

# 从 backend.models 中导入所有模型，确保 Alembic 能检测到它们
# !!! 确保这里导入了所有定义了 table=True 的模型 !!!
from backend import models 
# --- 新增部分结束 ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- 修改这里，使用我们自己的 settings ---
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL) # 使用 settings 中的同步 URL
# --- 修改结束 ---


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata # --- 修改这里，使用 SQLModel 的元数据 ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()