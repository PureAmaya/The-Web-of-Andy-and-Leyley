# backend/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, validator
from pathlib import Path
from typing import List, Optional  # 确保导入 List, Optional

ENV_PATH = Path(__file__).parent.parent / ".env"


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
    # 邮件配置
    MAIL_USERNAME: EmailStr = "your_email_username@example.com"
    MAIL_PASSWORD: str = "your_super_secret_email_password"
    MAIL_FROM: EmailStr = "noreply@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.example.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = "我的门户网站"

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

    # 使用 @property 来动态构建数据库 URL
    _ASYNC_DATABASE_URL: Optional[str] = None
    _SYNC_DATABASE_URL: Optional[str] = None

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


try:
    settings = Settings()
    print("DEBUG: [config.py] Settings object created successfully.")
    print(f"DEBUG: [config.py] Loaded POSTGRES_USER from settings: {settings.POSTGRES_USER}")
except Exception as e:
    print(f"DEBUG: [config.py] Error creating Settings instance: {e}")
    raise # 重新抛出异常，以便看到原始的 Pydantic 错误