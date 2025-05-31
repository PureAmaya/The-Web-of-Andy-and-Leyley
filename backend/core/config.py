# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
from pathlib import Path # <--- 1. 导入 Path

# 2. 定义 .env 文件的路径
#    Path(__file__) 是当前 config.py 文件的路径
#    .parent 是父目录 (即 core/ 文件夹)
#    .parent.parent 是父目录的父目录 (即 backend/ 文件夹)
#    然后我们在这个 backend/ 目录下寻找 .env 文件
ENV_PATH = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    # 邮件配置
    MAIL_USERNAME: EmailStr = "your_email_username@example.com"
    MAIL_PASSWORD: str = "your_super_secret_email_password"
    MAIL_FROM: EmailStr = "noreply@example.com"
    MAIL_PORT: int = 587  # 通常是 587 (TLS) 或 465 (SSL)
    MAIL_SERVER: str = "smtp.example.com" # 你的邮件服务器地址
    MAIL_STARTTLS: bool = True # 如果 MAIL_PORT 是 587，通常为 True
    MAIL_SSL_TLS: bool = False # 如果 MAIL_PORT 是 465，通常为 True
    MAIL_FROM_NAME: str = "我的门户网站"

    # 邮件验证令牌相关 (从 auth_utils.py 移到这里集中管理更佳)
    EMAIL_VERIFICATION_SECRET_KEY: str = "a-very-secret-key-for-email-that-should-be-in-env"
    EMAIL_VERIFICATION_SALT: str = "email-verification-salt-that-should-be-in-env"
    EMAIL_TOKEN_MAX_AGE_SECONDS: int = 3600

    # 门户网站前端基础 URL (用于构建验证链接)
    # 例如：Vue.js 前端运行在 http://localhost:5173
    PORTAL_FRONTEND_BASE_URL: str = "http://localhost:5173"

    # --- 新增：密码重置令牌配置 ---
    PASSWORD_RESET_SECRET_KEY: str = "a-very-secret-key-for-password-reset"  # 必须非常强壮且保密
    PASSWORD_RESET_SALT: str = "password-reset-salt"  # 独立的盐值
    PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS: int = 900  # 密码重置令牌有效期，例如15分钟 (900秒)

    # JWT 密钥 (为未来登录功能预留)
    JWT_SECRET_KEY: str = "jwt-secret-key-example"
    JWT_REFRESH_SECRET_KEY: str = "jwt-refresh-secret-key-example"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

# 为了方便，确保 auth_utils.py 中的令牌配置也使用这里的 settings 对象
# 例如，在 auth_utils.py 中:
# from core.config import settings
# EMAIL_VERIFICATION_SECRET_KEY = settings.EMAIL_VERIFICATION_SECRET_KEY
# EMAIL_VERIFICATION_SALT = settings.EMAIL_VERIFICATION_SALT
# EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS = settings.EMAIL_TOKEN_MAX_AGE_SECONDS