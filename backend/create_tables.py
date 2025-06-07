# backend/create_tables.py
import os
from pathlib import Path
from sqlmodel import SQLModel

from backend.core.config import settings
# 使用 database.py 中定义的同步引擎和创建函数
from database import sync_engine as engine # 使用重命名的同步引擎
from database import create_db_and_tables_sync # 使用新的同步创建函数
# 或者，如果 create_db_and_tables_sync 直接在 database.py 中操作全局的 sync_engine:
# from database import create_db_and_tables_sync, settings # 可能需要 settings 来打印DB名

# !!! 非常重要：在这里导入所有定义了 table=True 的模型 !!!
from models import User, VerificationToken, PasswordResetToken, GalleryItem, Member

def init_db(delete_existing_db: bool = False): # delete_existing_db 对PostgreSQL意义不大
    print("开始初始化 PostgreSQL 数据库表...")

    if delete_existing_db:
        print("警告：对于PostgreSQL，`--delete-db` 选项不会删除数据库本身或表。")
        print("您需要手动使用数据库工具（如psql或pgAdmin）来DROP和CREATE数据库或表。")
        print("此脚本将尝试在现有数据库上创建表（如果它们不存在）。")

    print("正在创建所有表...")
    try:
        # SQLModel.metadata.create_all(engine) # 直接调用 database.py 中的函数
        create_db_and_tables_sync()
        print(f"所有表已在数据库 '{settings.POSTGRES_DB}' 上成功创建/检查。")

    except Exception as e:
        print(f"创建表时发生严重错误: {e}")
        # ... (其他错误处理保持不变) ...
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="初始化 PostgreSQL 数据库并根据 SQLModel 模型创建表结构。")
    parser.add_argument(
        "--delete-db", # 这个参数对于PostgreSQL的行为会有所不同
        action="store_true",
        help="对于PostgreSQL，此选项仅作提示，不会自动删除数据库或表。请手动管理。"
    )
    args = parser.parse_args()

    print("--------------------------------------------------------------------")
    print("此脚本将尝试根据您的 SQLModel 模型在 PostgreSQL 数据库中创建表结构。")
    print(f"目标数据库: {settings.POSTGRES_DB} 在服务器 {settings.POSTGRES_SERVER}")
    if args.delete_db:
        print("提示：--delete-db 对于PostgreSQL意味着您应该在运行此脚本前手动清理数据库/表（如果需要）。")
    print("--------------------------------------------------------------------")

    confirm = input("是否继续执行数据库初始化? (yes/no): ")
    if confirm.lower() == 'yes':
        init_db(delete_existing_db=args.delete_db) # 传递参数
    else:
        print("数据库初始化已取消。")