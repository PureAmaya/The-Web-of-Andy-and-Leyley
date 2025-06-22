# backend/auth_utils.py
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlmodel import select # 导入 select
from sqlmodel.ext.asyncio.session import AsyncSession # 确保导入 AsyncSession

from backend.core.config import get_settings
from backend.database import get_async_session # 修改为依赖 get_async_session
from backend.models import TokenData, User, UserRole

settings = get_settings()
logger = logging.getLogger(__name__)

# --- OAuth2PasswordBearer Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # 调整为 /auth/token

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
        return None
    except Exception as e:
        logger.error(f"验证邮件令牌时发生未知错误: {e}")
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
        return None
    except Exception as e:
        logger.error(f"验证密码重置令牌时发生未知错误: {e}")
        return None


# --- JWT 令牌处理 ---
def _create_jwt_token(data: dict, secret_key: str, expires_delta: timedelta,
                      algorithm: str = settings.JWT_ALGORITHM) -> str:
    to_encode = data.copy()
    # JWT 的 'exp' 字段通常是 Unix 时间戳，它是时区无关的。
    # datetime.now(timezone.utc) 是正确的，因为这确保 exp 是基于 UTC 的。
    # 此处不需要 .replace(tzinfo=None)
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
            logger.debug("Token payload missing 'sub_id'")
            return None

        token_data = TokenData(user_id=int(user_id_from_payload))
        return token_data
    except JWTError as e:
        logger.debug(f"JWT 错误: {e}")
        return None
    except (ValueError, ValidationError) as e:
        logger.debug(f"TokenData 构造或校验错误: {e}")
        return None


def verify_access_token_and_get_token_data(token: str) -> Optional[TokenData]:
    return _verify_jwt_and_get_token_data(token, settings.JWT_SECRET_KEY)


def verify_refresh_token_and_get_token_data(token: str) -> Optional[TokenData]:
    return _verify_jwt_and_get_token_data(token, settings.JWT_REFRESH_SECRET_KEY)


# --- 获取当前用户依赖项 ---
async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme)
) -> TokenData:
    """
    依赖项：验证JWT访问令牌并返回令牌内的数据 (TokenData)。
    如果令牌无效或过期，则抛出401异常。
    """
    token_data = verify_access_token_and_get_token_data(token)
    if not token_data or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据 (令牌无效、已过期或格式错误)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


async def get_current_active_user(
        token_data: TokenData = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_async_session) # 依赖 AsyncSession
) -> User:
    """
    依赖项：从已验证的访问令牌中获取当前用户，并检查用户是否处于活动状态。
    如果令牌无效、用户不存在或用户非活动，则抛出异常。
    """
    # 使用异步方式从数据库获取用户
    result = await session.exec(select(User).where(User.id == token_data.user_id))
    user = result.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="与令牌关联的用户未找到")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用")
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    依赖项：获取当前用户，并验证其是否为管理员。
    如果不是管理员，则抛出403 Forbidden异常。
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够权限执行此操作"
        )
    return current_user