# backend/create_tables.py
import os  # 用于删除旧的数据库文件（可选）
from pathlib import Path  # 用于构建数据库文件路径

# 首先确保 SQLModel 和 engine 被正确导入和配置
# 这里的导入路径取决于您的 database.py 文件相对于 create_tables.py 的位置
# 假设它们都在 backend 文件夹下
from database import engine, DATABASE_FILE_PATH  # 确保 DATABASE_FILE_PATH 在 database.py 中已定义并导出
from sqlmodel import SQLModel

# !!! 非常重要：在这里导入所有定义了 table=True 的模型 !!!
# 这样 SQLModel.metadata 才能知道这些表的存在。
# 确保这里的导入路径相对于 create_tables.py 是正确的。
from models import User, VerificationToken, PasswordResetToken  # 以及您项目中其他所有表模型


def init_db():
    print("开始初始化数据库...")

    # 可选：在创建表之前删除旧的数据库文件，以确保完全重新创建
    # 这在开发初期，当模型频繁更改时非常有用
    # 在生产环境中，您不应该这样做，而应该使用数据库迁移工具
    if DATABASE_FILE_PATH.exists():
        try:
            print(f"发现已存在的数据库文件: {DATABASE_FILE_PATH}")
            # confirm_delete = input(f"是否删除已存在的数据库文件 {DATABASE_FILE_PATH} 以重新创建? (yes/no): ")
            # if confirm_delete.lower() == 'yes':
            #     os.remove(DATABASE_FILE_PATH)
            #     print(f"数据库文件 {DATABASE_FILE_PATH} 已删除。")
            # else:
            #     print("保留现有数据库文件。如果表结构已存在，create_all 可能不会执行任何操作或因冲突报错。")
            #     # 如果保留现有文件，并且模型有 __table_args__ = {'extend_existing': True}，
            #     # 那么 create_all 应该尝试扩展而不是报错。
            #     # 但为了解决您遇到的持久性错误，建议从干净的数据库开始。
            #     # 为了自动化此脚本，我们暂时跳过交互式确认，但保留删除逻辑（您可以根据需要注释掉）
            print("为了确保从干净状态开始，建议在运行此脚本前手动删除旧的数据库文件。")
            print("当前脚本不会自动删除它，以防意外丢失数据。")
            print("如果旧文件存在且结构冲突，create_all 可能会失败。")


        except Exception as e:
            print(f"删除数据库文件时发生错误: {e}")
            # 如果删除失败，后续的 create_all 可能仍然会遇到问题

    print("正在创建所有表...")
    try:
        # 确保所有模型在调用此函数之前都已被导入并注册到 SQLModel.metadata
        SQLModel.metadata.create_all(engine)
        print("所有表已成功创建 (或者已存在且结构兼容)。")
        if not DATABASE_FILE_PATH.exists():
            print(f"注意：数据库文件 {DATABASE_FILE_PATH} 似乎未被创建，请检查路径和权限。")
        else:
            print(f"数据库文件位于: {DATABASE_FILE_PATH}")

    except Exception as e:
        print(f"创建表时发生严重错误: {e}")
        print("请检查您的模型定义和数据库连接。")
        print("如果错误是关于 'table already defined' 或 'index already exists'，")
        print("并且您认为是从干净的数据库开始的，请仔细检查 models.py 中的 __table_args__ 设置，")
        print("以及是否有重复的 UniqueConstraint 或不当的 index=True/unique=True 组合。")
        raise


if __name__ == "__main__":
    print("--------------------------------------------------------------------")
    print("此脚本将尝试根据您的 SQLModel 模型在数据库中创建表结构。")
    print(f"目标数据库文件: {DATABASE_FILE_PATH}")
    print("--------------------------------------------------------------------")

    confirm = input("是否继续执行数据库初始化? (yes/no): ")
    if confirm.lower() == 'yes':
        init_db()
    else:
        print("数据库初始化已取消。")
