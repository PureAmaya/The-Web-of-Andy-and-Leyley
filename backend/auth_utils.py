# backend/auth_utils.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pydantic import ValidationError  # 用于捕获 TokenData 的校验错误

# 假设这些可以从您的项目中正确导入
from backend.core.config import settings  # 导入 settings 对象
from backend.models import TokenData, User  # 导入 Pydantic/SQLModel 模型
from backend.database import get_session  # 导入 get_session 依赖
from sqlmodel import Session, select  # 导入 SQLModel Session 和 select

# --- OAuth2PasswordBearer Scheme ---
# tokenUrl 指向我们获取令牌的端点路径 (即登录端点)
# 注意：根据您的 main.py 中的路由，这个路径可能是 /auth/token 或 /api/v1/auth/token
# 请确保它与您在 main.py 中定义的登录端点路径一致。
# 如果您的登录端点是 /api/v1/auth/token (如 main.py 中 app.include_router 的 prefix 设置)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- 密码哈希上下文 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- 邮件验证令牌相关 ---
email_verification_serializer = URLSafeTimedSerializer(
    secret_key=settings.EMAIL_VERIFICATION_SECRET_KEY,
    salt=settings.EMAIL_VERIFICATION_SALT
)


def generate_email_verification_token(email: str) -> str:
    return email_verification_serializer.dumps(email)


def verify_email_verification_token(token: str) -> Optional[str]:
    try:
        email = email_verification_serializer.loads(
            token,
            max_age=settings.EMAIL_TOKEN_MAX_AGE_SECONDS
        )
        return email
    except (SignatureExpired, BadTimeSignature):
        # 可以根据需要添加日志记录
        return None
    except Exception as e:
        print(f"验证邮件令牌时发生未知错误: {e}")
        return None


# --- 密码重置令牌相关 ---
password_reset_serializer = URLSafeTimedSerializer(
    secret_key=settings.PASSWORD_RESET_SECRET_KEY,
    salt=settings.PASSWORD_RESET_SALT
)


def generate_password_reset_token(email: str) -> str:
    return password_reset_serializer.dumps(email)


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        email = password_reset_serializer.loads(
            token,
            max_age=settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS
        )
        return email
    except (SignatureExpired, BadTimeSignature):
        # 可以根据需要添加日志记录
        return None
    except Exception as e:
        print(f"验证密码重置令牌时发生未知错误: {e}")
        return None


# --- JWT 令牌处理 ---
def _create_jwt_token(data: dict, secret_key: str, expires_delta: timedelta,
                      algorithm: str = settings.JWT_ALGORITHM) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_jwt_token(data=data, secret_key=settings.JWT_SECRET_KEY, expires_delta=expires_delta)


def create_refresh_token(data: dict) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_jwt_token(data=data, secret_key=settings.JWT_REFRESH_SECRET_KEY, expires_delta=expires_delta)


def _verify_jwt_and_get_token_data(token: str, secret_key: str, algorithm: str = settings.JWT_ALGORITHM) -> Optional[
    TokenData]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id_from_payload = payload.get("sub_id")
        if user_id_from_payload is None:
            # print("Token payload missing 'sub_id'") # 调试信息
            return None

        # 确保 user_id 能被正确转换为整数并构造成 TokenData
        token_data = TokenData(user_id=int(user_id_from_payload))
        return token_data
    except JWTError as e:  # 包括 ExpiredSignatureError, InvalidSignatureError 等
        # print(f"JWT 错误: {e}") # 调试信息
        return None
    except (ValueError, ValidationError) as e:  # 捕获 int() 转换错误或 Pydantic 校验错误
        # print(f"TokenData 构造或校验错误: {e}") # 调试信息
        return None


def verify_access_token_and_get_token_data(token: str) -> Optional[TokenData]:
    return _verify_jwt_and_get_token_data(token, settings.JWT_SECRET_KEY)


def verify_refresh_token_and_get_token_data(token: str) -> Optional[TokenData]:
    return _verify_jwt_and_get_token_data(token, settings.JWT_REFRESH_SECRET_KEY)


# --- 获取当前用户依赖项 ---
async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme)  # 从 Authorization header 提取 Bearer token
) -> TokenData:
    """
    依赖项：验证JWT访问令牌并返回令牌内的数据 (TokenData)。
    如果令牌无效或过期，则抛出401异常。
    """
    token_data = verify_access_token_and_get_token_data(token)
    if not token_data or token_data.user_id is None:  # 确保 user_id 存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据 (令牌无效、已过期或格式错误)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


async def get_current_active_user(
        token_data: TokenData = Depends(get_current_user_from_token),
        session: Session = Depends(get_session)  # 使用从 database.py 导入的同步 get_session
        # 如果您的应用完全异步，这里应该依赖异步 get_async_session
) -> User:
    """
    依赖项：从已验证的访问令牌中获取当前用户，并检查用户是否处于活动状态。
    如果令牌无效、用户不存在或用户非活动，则抛出异常。
    """
    # 注意：由于 get_session 是同步的，而此函数是异步的，
    # 实际的数据库调用 session.get() 应该在 FastAPI 的线程池中执行以避免阻塞。
    # FastAPI 会自动处理同步函数依赖在异步路径操作中的情况。
    # 如果您将 get_session 也改为异步的 get_async_session，那么这里也需要 await。

    user = session.get(User, token_data.user_id)  # 同步调用
    # 对于异步会话，会是: user = await session.get(User, token_data.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="与令牌关联的用户未找到")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用")
    return user