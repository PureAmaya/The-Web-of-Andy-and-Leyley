﻿# backend/core/config.py
import logging
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, validator
from pathlib import Path
from typing import List, Optional  # 确保导入 List, Optional

ENV_PATH = Path(__file__).parent.parent / ".env"
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


# --- 2. 定义默认 .env 文件的模板内容 ---
# 注意：密钥部分使用了 {变量名} 作为占位符
DEFAULT_ENV_CONTENT = """
# =========================================================================
#  这是一个自动生成的 .env 配置文件。
#  请根据你的实际情况修改数据库和邮件服务器的配置。
#  所有 SECRET KEY 都已自动生成为安全随机值，建议直接使用。
# =========================================================================

# --- PostgreSQL 数据库配置 ---
POSTGRES_USER="your_db_user"
POSTGRES_PASSWORD="your_db_password"
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_DB="leyley_mc_db"

# --- 应用密钥 (自动生成) ---
JWT_SECRET_KEY="{jwt_secret}"
JWT_REFRESH_SECRET_KEY="{jwt_refresh_secret}"
EMAIL_VERIFICATION_SECRET_KEY="{email_verification_secret}"
EMAIL_VERIFICATION_SALT="{email_verification_salt}"
PASSWORD_RESET_SECRET_KEY="{password_reset_secret}"
PASSWORD_RESET_SALT="{password_reset_salt}"
SESSION_SECRET_KEY="{session_secret}"

# --- 邮件服务器配置 (示例) ---
MAIL_USERNAME="noreply@example.com"
MAIL_PASSWORD="your_email_password"
MAIL_FROM="noreply@example.com"
MAIL_SERVER="smtp.example.com"
MAIL_PORT=465
MAIL_FROM_NAME="安迪和莉莉的网站"
MAIL_STARTTLS=False
MAIL_SSL_TLS=True

# --- 应用行为 ---
PORTAL_FRONTEND_BASE_URL="http://localhost:5173"
ENABLE_REGISTRATION=true
CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
UPLOAD_MAX_SIZE_MB=50
GALLERY_DEFAULT_PAGE_SIZE=12
GALLERY_MAX_PAGE_SIZE=100
MC_AVATAR_URL_TEMPLATE="https://cravatar.eu/avatar/{{username}}/128.png"
"""

def generate_default_env_if_missing():
    """
    检查 .env 文件是否存在。如果不存在，则创建一个包含默认值和新生成密钥的文件。
    """
    if not ENV_PATH.exists():
        logger.warning(f"警告: 在路径 {ENV_PATH} 未找到 .env 文件。正在创建默认配置文件...")

        # 为所有密钥生成新的安全随机值
        generated_secrets = {
            "jwt_secret": secrets.token_hex(32),
            "jwt_refresh_secret": secrets.token_hex(32),
            "email_verification_secret": secrets.token_hex(32),
            "email_verification_salt": secrets.token_hex(16),
            "password_reset_secret": secrets.token_hex(32),
            "password_reset_salt": secrets.token_hex(16),
            "session_secret": secrets.token_hex(32),
        }

        # 将生成的密钥填入模板
        content = DEFAULT_ENV_CONTENT.format(**generated_secrets)

        try:
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(content.strip() + '\n')
            logger.info(f"成功创建默认的 .env 文件于: {ENV_PATH}")
            logger.warning("重要提示: 请打开新生成的 .env 文件，并更新你的数据库和邮件服务器配置信息！")
        except IOError as e:
            logger.error(f"创建 .env 文件失败: {e}")

# --- 4. 在模块加载时立即执行这个检查 ---
generate_default_env_if_missing()

# --- 添加调试打印 ---
print(f"DEBUG: [config.py] __file__ is: {__file__}")
print(f"DEBUG: [config.py] Calculated ENV_PATH: {ENV_PATH}")
print(f"DEBUG: [config.py] Does .env file exist at ENV_PATH? {ENV_PATH.exists()}")
if ENV_PATH.exists():
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            print(f"DEBUG: [config.py] Content of .env file (first few lines):")
            for i, line in enumerate(f):
                if i < 15: # 只打印前15行以避免过长的输出
                    print(f"  {line.strip()}")
                else:
                    break
    except Exception as e:
        print(f"DEBUG: [config.py] Error reading .env file: {e}")
# --- 结束调试打印 ---

class Settings(BaseSettings):
    SESSION_SECRET_KEY: str

    # 邮件配置
    MAIL_USERNAME: EmailStr = "your_email_username@example.com"
    MAIL_PASSWORD: str = "your_super_secret_email_password"
    MAIL_FROM: EmailStr = "noreply@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.example.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = "安迪和莉莉的网站"

    # 邮件验证令牌相关
    EMAIL_VERIFICATION_SECRET_KEY: str
    EMAIL_VERIFICATION_SALT: str
    EMAIL_TOKEN_MAX_AGE_SECONDS: int = 3600

    # 门户网站前端基础 URL
    PORTAL_FRONTEND_BASE_URL: str = "http://localhost:5173"

    # 密码重置令牌配置
    PASSWORD_RESET_SECRET_KEY: str
    PASSWORD_RESET_SALT: str
    PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS: int = 900

    # JWT 密钥
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- PostgreSQL 配置 ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # 开放注册
    ENABLE_REGISTRATION: bool = True  # 默认为开启

    #其他的一些配置
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173"
    UPLOAD_ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,image/gif,video/mp4"
    UPLOAD_MAX_SIZE_MB: int = 50
    GALLERY_DEFAULT_PAGE_SIZE: int = 12
    GALLERY_MAX_PAGE_SIZE: int = 100
    MC_AVATAR_URL_TEMPLATE: str = "https://cravatar.eu/avatar/{username}/128.png"


    # 使用 @property 来动态构建数据库 URL
    _ASYNC_DATABASE_URL: Optional[str] = None
    _SYNC_DATABASE_URL: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(',')]

    @property
    def allowed_mime_types_list(self) -> List[str]:
        return [mime_type.strip() for mime_type in self.UPLOAD_ALLOWED_MIME_TYPES.split(',')]

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        if self._ASYNC_DATABASE_URL is None:
            self._ASYNC_DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self._ASYNC_DATABASE_URL

    @property
    def SYNC_DATABASE_URL(self) -> str:  # 同步URL，用于 Alembic 或 create_tables.py
        if self._SYNC_DATABASE_URL is None:
            # psycopg2 (binary) 驱动的连接字符串通常只是 "postgresql://"
            self._SYNC_DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self._SYNC_DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )


_cached_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    获取配置对象的函数，使用了缓存以提高性能。
    这是实现动态重载的关键。
    """
    global _cached_settings
    if _cached_settings is None:
        _cached_settings = Settings()
        print("DEBUG: [config.py] Settings object (re)loaded.")
    return _cached_settings

def clear_settings_cache():
    """清除配置缓存，以便下次调用 get_settings 时重新加载。"""
    global _cached_settings
    _cached_settings = None
    print("DEBUG: [config.py] Settings cache cleared.")
