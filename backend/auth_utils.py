# auth_utils.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from typing import Optional
import os

from backend.models import TokenData
from core.config import settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from database import get_session
from pydantic import ValidationError
from sqlmodel import Session, select
from models import TokenData, User

# --- OAuth2PasswordBearer Scheme ---
# tokenUrl 指向我们获取令牌的端点路径 (即登录端点)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") # <--- 5. 定义 oauth2_scheme


# 1. 创建一个 CryptContext 实例
#    我们告诉它我们想使用 "bcrypt" 作为默认的（也是唯一的）哈希方案。
#    `deprecated="auto"` 会自动处理旧的哈希格式（如果将来我们改变方案的话）。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与存储的哈希密码匹配。

    Args:
        plain_password: 用户输入的明文密码。
        hashed_password: 数据库中存储的哈希密码。

    Returns:
        如果密码匹配则返回 True，否则返回 False。
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    为给定的明文密码生成哈希值。

    Args:
        password: 需要哈希的明文密码。

    Returns:
        密码的哈希字符串。
    """
    return pwd_context.hash(password)

# --- 新增：邮件验证令牌相关 ---

# 2. 配置令牌参数
EMAIL_VERIFICATION_SECRET_KEY = settings.EMAIL_VERIFICATION_SECRET_KEY
EMAIL_VERIFICATION_SALT = settings.EMAIL_VERIFICATION_SALT
EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS = settings.EMAIL_TOKEN_MAX_AGE_SECONDS


# 3. 创建 URLSafeTimedSerializer 实例
# 这个序列化器会创建包含时间戳并使用密钥和盐进行签名的令牌。
email_verification_serializer = URLSafeTimedSerializer(
    secret_key=EMAIL_VERIFICATION_SECRET_KEY,
    salt=EMAIL_VERIFICATION_SALT
)

def generate_email_verification_token(email: str) -> str:
    """
    为给定的邮箱地址生成一个有时限的、安全的邮件验证令牌。

    Args:
        email: 需要嵌入到令牌中的用户邮箱地址。

    Returns:
        生成的邮件验证令牌字符串。
    """
    return email_verification_serializer.dumps(email)

def verify_email_verification_token(token: str) -> Optional[str]:
    """
    验证邮件验证令牌的有效性（签名和有效期）。

    Args:
        token: 从用户处接收到的令牌字符串。

    Returns:
        如果令牌有效且未过期，则返回嵌入的邮箱地址 (str)。
        如果令牌无效、签名错误或已过期，则返回 None。
    """
    try:
        # max_age 参数会检查令牌是否在指定时间内创建
        email = email_verification_serializer.loads(
            token,
            max_age=EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS
        )
        return email
    except SignatureExpired:
        # 令牌已过期
        print("邮件验证令牌已过期。")
        return None
    except BadTimeSignature:
        # 令牌签名无效（可能被篡改或密钥/盐不匹配）
        print("邮件验证令牌签名无效。")
        return None
    except Exception as e:
        # 其他可能的 itsdangerous 错误
        print(f"验证邮件令牌时发生未知错误: {e}")
        return None


# --- 更新/确认 verify_token_and_get_data (或创建一个专门用于访问令牌的) ---
def verify_access_token_and_get_token_data(token: str) -> Optional[TokenData]:
    """
    验证访问令牌并从中提取 TokenData。
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY, # 使用访问令牌的密钥
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_from_payload = payload.get("sub_id")
        if user_id_from_payload is None:
            raise JWTError("User ID (sub_id) not in token payload")

        # 使用 TokenData 模型进行数据校验 (可选但推荐)
        token_data = TokenData(user_id=int(user_id_from_payload))
        return token_data
    except JWTError as e: # 包括 TokenExpiredError, InvalidSignatureError 等
        print(f"访问令牌验证错误: {e}")
        return None
    except ValueError: # 如果 int(user_id_from_payload) 失败
         print(f"访问令牌中的 user_id 格式无效")
         return None
    except ValidationError as e: # 如果 Pydantic 的 TokenData 校验失败
        print(f"令牌数据校验失败: {e}")
        return None



# --- 新增：密码重置令牌相关 ---
# 1. 从 settings 获取密码重置令牌的配置 (这些需要在 core/config.py 和 .env 中定义)
PASSWORD_RESET_SECRET_KEY = settings.PASSWORD_RESET_SECRET_KEY
PASSWORD_RESET_SALT = settings.PASSWORD_RESET_SALT
PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS = settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS

# 2. 创建专门用于密码重置令牌的 URLSafeTimedSerializer 实例
password_reset_serializer = URLSafeTimedSerializer(
    secret_key=PASSWORD_RESET_SECRET_KEY,
    salt=PASSWORD_RESET_SALT
)

def generate_password_reset_token(email: str) -> str:
    """
    为给定的邮箱地址生成一个有时限的、安全的密码重置令牌。
    """
    return password_reset_serializer.dumps(email)

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌的有效性（签名和有效期）。
    如果有效，返回嵌入的邮箱地址。
    """
    try:
        email = password_reset_serializer.loads(
            token,
            max_age=PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS
        )
        return email
    except SignatureExpired:
        print("密码重置令牌已过期。")
        return None
    except BadTimeSignature:
        print("密码重置令牌签名无效。")
        return None
    except Exception as e:
        print(f"验证密码重置令牌时发生未知错误: {e}")
        return None


# --- 新增：JWT 令牌处理 ---

def create_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta) -> str:
    """
    通用的令牌创建函数。
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_access_token(data: dict) -> str:
    """
    创建 JWT 访问令牌。
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(
        data=data,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=expires_delta
    )


def create_refresh_token(data: dict) -> str:
    """
    创建 JWT 刷新令牌。
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(
        data=data,
        secret_key=settings.JWT_REFRESH_SECRET_KEY,  # 使用不同的密钥以增强安全性
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=expires_delta
    )


def verify_token_and_get_data(token: str, secret_key: str, algorithm: str) -> Optional[TokenData]:
    """
    通用的令牌验证和数据提取函数。
    如果令牌无效或过期，则返回 None。
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id_from_payload = payload.get("sub_id")  # 我们将使用 "sub_id" 作为 user_id 的声明
        if user_id_from_payload is None:
            # 如果令牌中没有 user_id (或你选择的其他标识符)，则认为令牌无效
            return None
        # username_from_payload = payload.get("sub_name") # 如果也存了 username

        # 校验 'exp' 声明是否仍然有效 (虽然 jwt.decode 也会检查)
        # exp = payload.get("exp")
        # if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        #     return None # 已过期

        return TokenData(user_id=int(user_id_from_payload))  # 假设 user_id 是整数
    except JWTError as e:
        print(f"JWT 错误: {e}")  # 例如 token 过期、签名无效等
        return None
    except Exception as e:  # 捕获其他可能的转换错误，例如 int()
        print(f"验证令牌时发生意外错误: {e}")
        return None


# --- 6. 新增：get_current_active_user 依赖项 ---
async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme) # 从 Authorization header 提取 Bearer token
) -> TokenData:
    """
    依赖项：验证JWT访问令牌并返回令牌内的数据 (TokenData)。
    如果令牌无效或过期，则抛出401异常。
    """
    token_data = verify_access_token_and_get_token_data(token)
    if not token_data or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据 (令牌无效或已过期)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# 注意: get_session 依赖需要能被这里访问到。
# 如果 get_session 在 main.py 中，我们需要在 main.py 中组装 get_current_active_user，
# 或者将 get_session 移到可以被 auth_utils.py 导入的地方 (例如 database.py 或 deps.py)。
# 假设我们将在 main.py 中定义 get_session，并在那里传递它。
# 为了模块化，更好的做法是将 get_session 放在一个可共享的地方。
# 暂时，我们让 get_current_active_user 依赖于一个 Session 对象，
# 这个 Session 对象将由 FastAPI 通过另一个依赖注入。

async def get_current_active_user(
    # session: Session = Depends(get_session), # 假设 get_session 可以被导入或已在 main 中定义
    # 为了让这个函数能在 auth_utils.py 中完整定义，
    # 并且能在 main.py 中被 Depends() 调用，我们需要一种方式获取 session。
    # 我们将修改它，使其依赖于 TokenData 和 Session。
    # Session 将通过 Depends(get_session) 在 main.py 的端点中注入。
    # TokenData 将通过 Depends(get_current_user_from_token) 注入。
    #
    # 重构思路：
    # get_current_user_from_token: 从 header 获取 token 字符串 -> 验证 -> 返回 TokenData
    # get_current_active_user: 依赖 get_current_user_from_token 和 get_session -> 从 TokenData 取 user_id -> DB 查询 -> 返回 User
    #
    # 所以，get_current_active_user 的签名应该是这样的：
    token_data: TokenData = Depends(get_current_user_from_token),
    # session: Session = Depends(...) # Session 依赖需要在实际端点中提供
    #
    # 为了简化，我们直接在这里组合。
    # 最终在端点中会这样用: current_user: User = Depends(get_current_active_user)
    # 而 get_current_active_user 内部会处理 token 和 session。
    #
    # 正确的模块化做法是让 get_current_active_user 依赖于 get_session
    # 如果 get_session 在 main.py, 我们可以在 main.py 中定义一个包装器
    # 或者将 get_session 移到 database.py 并从那里导入。
    #
    # 假设 get_session() 已经可以从 database.py 导入:
    # from database import get_session # 假设我们把它移到了那里
    # session: Session = Depends(get_session), # 取消注释这一行，如果 get_session 可用
    #
    # 如果保持 get_session 在 main.py，那么 get_current_active_user 自身不能直接依赖它
    # 而是 main.py 中的端点会这样写：
    # async def my_protected_route(session: Session = Depends(get_session), current_user: User = Depends(get_user_object_from_token_data_and_session)):
    #
    # 为了简单起见，我们先创建一个版本，它只返回 User ID，实际的数据库查询在端点中进行。
    # 或者，更常见的是，get_current_active_user *确实* 进行数据库查询。
    # 我们需要 get_session。假设它现在在 database.py (这是个好位置)。
    #
    # **修改 database.py**
    # 在 database.py 中添加 (如果还没有):
    # from sqlmodel import Session, create_engine # create_engine 应该已存在
    # engine = ... # 应该已存在
    # def get_session():
    #     with Session(engine) as session:
    #         yield session
    #

    session: Session = Depends(get_session)
) -> User: # 返回 User 模型实例
    """
    依赖项：从已验证的访问令牌中获取当前用户，并检查用户是否处于活动状态。
    如果令牌无效、用户不存在或用户非活动，则抛出异常。
    """
    if not token_data.user_id: # 双重检查，虽然 get_current_user_from_token 应该已处理
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无法验证用户ID")

    user = session.get(User, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未找到")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用")
    # 根据文档，登录时检查了 is_verified。访问受保护资源时，通常只检查 is_active。
    # 如果也需要检查 is_verified:
    # if not user.is_verified:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱未验证")
    return user


# --- 新增：刷新令牌验证函数 ---
def verify_refresh_token_and_get_token_data(token: str) -> Optional[TokenData]:
    """
    验证刷新令牌并从中提取 TokenData。
    使用 JWT_REFRESH_SECRET_KEY。
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_REFRESH_SECRET_KEY, # <--- 使用刷新令牌的密钥
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_from_payload = payload.get("sub_id")
        if user_id_from_payload is None:
            raise JWTError("User ID (sub_id) not in refresh token payload")

        token_data = TokenData(user_id=int(user_id_from_payload))
        return token_data
    except JWTError as e:
        print(f"刷新令牌验证错误: {e}")
        return None
    except ValueError:
        print(f"刷新令牌中的 user_id 格式无效")
        return None
    except Exception as e: # 包括 Pydantic 的 ValidationError (如果 TokenData 更复杂)
        print(f"验证刷新令牌数据时发生意外错误: {e}")
        return None