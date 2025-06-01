# backend/main.py
import shutil
import uuid
from pathlib import Path
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import datetime  # 用于 datetime.datetime, datetime.timezone, datetime.timedelta
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlmodel import Session, select, SQLModel

# 项目内部模块导入
from database import create_db_and_tables, engine
from models import (
    User,
    UserCreate,
    UserRead,
    VerificationToken,
    Token,
    RefreshTokenRequest, UserPasswordUpdate, UserUpdate, PasswordResetRequest, PasswordResetToken, PasswordResetForm,
    GalleryItemCreate, GalleryItem, GalleryItemReadWithUploader
)
from auth_utils import (
    get_password_hash,
    generate_email_verification_token,
    verify_email_verification_token,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_refresh_token_and_get_token_data,
    get_current_active_user, generate_password_reset_token, verify_password_reset_token
)
from email_utils import send_verification_email, send_password_reset_email
from core.config import settings
from PIL import Image as PILImage  # <--- 1. 导入 Pillow 的 Image 模块
from PIL.Image import Resampling  # <--- 1.1 导入 Resampling (Pillow 9.1.0+)
import io  # 用于处理图片字节流

# --- 定义上传文件存储的临时目录 (后续会根据存储策略调整) ---
# 确保这个目录存在，或者在应用启动时创建它
# 为了安全，这个目录不应该直接对外暴露通过HTTP访问
UPLOAD_DIR = Path("backend/uploads")  # 假设在 backend 文件夹下创建一个 uploads 目录
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 创建目录（如果不存在）
GALLERY_TAGS = ["Gallery"]  # 为画廊相关端点定义标签


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用的 lifespan 管理器。
    在应用启动时创建数据库表。
    """
    print("应用启动中...")
    # create_db_and_tables()
    print("数据库表已检查/创建。")
    yield  # 应用在此处运行
    print("应用关闭中...")


app = FastAPI(
    title="我的门户网站 API",
    version="0.1.0",
    lifespan=lifespan
)

# --- CORS 中间件设置 ---
origins = [
    settings.PORTAL_FRONTEND_BASE_URL,  # 从配置中读取前端地址
    "http://localhost",  # 通用本地开发
]
# 去重并过滤空值（如果 PORTAL_FRONTEND_BASE_URL 未设置或与其他重复）
# origins = list(filter(None, set(origins)))
# if not origins: # 如果列表为空，至少允许一个，例如本地开发时的通用端口
#     origins = ["http://localhost:5173"]


# --- 2. 挂载静态文件目录 ---
# 这会使得 UPLOAD_DIR 目录下的所有文件可以通过 /uploads 这个 URL 路径前缀访问
# 例如，如果 UPLOAD_DIR 中有一个文件 a.jpg，那么它可以通过 http://localhost:8000/uploads/a.jpg 访问
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(o for o in origins if o)),  # 确保列表唯一且不含 None/空字符串
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 数据库会话依赖 ---
def get_session():
    """
    依赖项：为每个请求提供一个数据库会话，并在请求完成后关闭它。
    """
    with Session(engine) as session:
        yield session


# --- 根路径 ---
@app.get("/", tags=["General"])
async def read_root():
    """
    根路径，返回一个欢迎信息。
    """
    return {"message": f"欢迎来到 {settings.MAIL_FROM_NAME} API"}


# --- 认证相关端点 ---
AUTH_TAGS = ["Authentication"]


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=AUTH_TAGS)
async def register_user(
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    """
    注册新用户:
    - 校验用户名和邮箱的唯一性。
    - 哈希用户密码。
    - 在数据库中创建新用户记录。
    - 生成并存储邮件验证令牌的哈希。
    - 通过后台任务发送验证邮件。
    """
    existing_user_by_username = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用",
        )

    existing_user_by_email = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )

    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        bio=user_create.bio,
        avatar_url=user_create.avatar_url,
        is_active=True,  # 新用户默认为激活
        is_verified=False,  # 等待邮件验证
        # created_at 和 updated_at 会使用 default_factory 自动填充
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    try:
        raw_email_token = generate_email_verification_token(db_user.email)
        token_hash_for_db = get_password_hash(raw_email_token)
        expires_delta = datetime.timedelta(seconds=settings.EMAIL_TOKEN_MAX_AGE_SECONDS)
        token_expires_at = datetime.datetime.now(datetime.timezone.utc) + expires_delta

        verification_token_db = VerificationToken(
            user_id=db_user.id,
            token_hash=token_hash_for_db,
            expires_at=token_expires_at
        )
        session.add(verification_token_db)
        session.commit()

        background_tasks.add_task(
            send_verification_email,
            email_to=db_user.email,
            username=db_user.username,
            token=raw_email_token
        )
        print(f"验证邮件任务已添加到后台队列，发送至 {db_user.email}")

    except Exception as e:
        print(f"创建用户 {db_user.username} 后，处理邮件验证时发生错误: {e}")
        # 错误处理：即使邮件发送失败，用户也已创建。可以考虑记录错误或后续处理。
        pass

    return db_user


@app.get("/auth/verify-email", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def verify_email_address(
        token: str,
        session: Session = Depends(get_session)
):
    """
    验证用户邮箱地址。
    用户点击邮件中的链接后会访问此端点。
    """
    email_from_token = verify_email_verification_token(token)
    if not email_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的验证令牌",
        )

    user = session.exec(select(User).where(User.email == email_from_token)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # 或400，表示令牌虽有效但找不到对应用户
            detail="未找到与此邮箱关联的用户",
        )

    if user.is_verified:
        return {"message": "邮箱已成功验证"}

    user.is_verified = True
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(user)  # 标记用户对象已更改

    # 使验证令牌失效或从数据库中删除
    token_hash_to_lookup = get_password_hash(token)
    db_token_record = session.exec(
        select(VerificationToken).where(VerificationToken.token_hash == token_hash_to_lookup)
    ).first()

    if db_token_record:
        if db_token_record.user_id == user.id:
            session.delete(db_token_record)
        else:
            # 令牌哈希匹配但用户ID不匹配，这是异常情况
            session.rollback()  # 回滚对 user.is_verified 的更改
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证令牌与用户不匹配，验证失败",
            )
    else:
        # 令牌本身有效（签名和时间），但在DB中未找到记录
        # 这可能意味着令牌已被使用或存储时出错
        # 根据业务需求，可以决定是否依然验证用户
        # 为安全起见，如果严格要求DB中有对应记录，这里应报错并回滚
        print(f"警告: 有效的签名令牌，但在数据库中未找到对应的令牌哈希记录。邮箱: {email_from_token}")
        # 如果需要严格检查，则取消下面两行注释:
        # session.rollback()
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证令牌记录未找到或已使用")
        pass  # 当前选择：如果签名令牌有效，即使DB无记录也允许通过（但留有警告）

    session.commit()  # 提交用户状态更新和令牌删除（如果找到）
    session.refresh(user)

    return {"message": "邮箱验证成功！您现在可以登录了。"}


@app.post("/auth/token", response_model=Token, tags=AUTH_TAGS)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    """
    用户登录以获取访问令牌和刷新令牌。
    需要 'username' (可以是邮箱或用户名) 和 'password' 通过表单数据提交。
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user:
        user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱/用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 或者 403 Forbidden
            detail="用户已被禁用，请联系管理员",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 或者 403 Forbidden
            detail="邮箱未验证，请先验证您的邮箱",
        )

    token_data_payload = {"sub_id": user.id}
    access_token = create_access_token(data=token_data_payload)
    refresh_token = create_refresh_token(data=token_data_payload)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# --- 10. 新增：受保护的端点示例 ---
USERS_TAGS = ["Users"]  # 为用户相关端点定义标签


@app.get("/users/me", response_model=UserRead, tags=USERS_TAGS)
async def read_users_me(
        current_user: User = Depends(get_current_active_user)  # <--- 2. 使用依赖项
):
    """
    获取当前登录用户的信息。
    需要有效的访问令牌。
    """
    # current_user 对象是由 get_current_active_user 依赖项返回的 User 模型实例
    # 它已经经过了令牌验证、数据库查询和活动状态检查。
    # FastAPI 会自动使用 UserRead 模型来序列化 current_user 以进行响应。
    return current_user


@app.get("/users/me/items", tags=USERS_TAGS)  # 另一个受保护端点的示例
async def read_own_items(
        current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户拥有的物品 (示例端点)。
    需要有效的访问令牌。
    """
    # 这里可以添加获取与 current_user.id 关联的物品的逻辑
    return {"message": f"用户 {current_user.username} (ID: {current_user.id}) 的物品列表", "items": []}


# --- 11. 新增：刷新令牌端点 ---
@app.post("/auth/refresh-token", response_model=Token, tags=AUTH_TAGS)
async def refresh_access_token(
        refresh_request: RefreshTokenRequest,  # <--- 3. 接收包含刷新令牌的请求体
        session: Session = Depends(get_session)
):
    """
    使用刷新令牌获取新的访问令牌。
    """
    refresh_token_str = refresh_request.refresh_token

    # 4. 验证刷新令牌
    token_data = verify_refresh_token_and_get_token_data(refresh_token_str)
    if not token_data or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5. （可选但推荐）检查用户是否存在且处于活动状态
    user = session.get(User, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="与此刷新令牌关联的用户不存在",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 使用 403 表示用户已知但被禁止
            detail="用户已被禁用",
        )
    # 如果在登录时检查了 is_verified，这里也可以考虑检查，但通常刷新令牌时主要关注用户是否还存在且活动。

    # 6. 生成新的访问令牌
    new_access_token_payload = {"sub_id": user.id}
    new_access_token = create_access_token(data=new_access_token_payload)

    # 7. 关于刷新令牌的轮换 (可选策略):
    #    - 策略1 (简单): 不轮换刷新令牌。旧的刷新令牌在有效期内仍然可用。
    #    - 策略2 (更安全): 每次使用刷新令牌时，都生成一个新的刷新令牌并使其旧的失效。
    #      这有助于减少刷新令牌被盗用后的风险窗口。如果采用此策略，需要将新的刷新令牌返回。
    #      我们的 Token 响应模型已包含 refresh_token 字段。
    #
    # 为了简单起见，我们先采用策略1：不轮换刷新令牌。
    # 如果要实现策略2，可以取消注释下面的代码：
    # new_refresh_token_payload = {"sub_id": user.id} # 或者可以包含其他用于追踪的信息
    # new_refresh_token = create_refresh_token(data=new_refresh_token_payload)
    # return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")

    return Token(
        access_token=new_access_token,
        refresh_token=refresh_token_str,  # 返回旧的刷新令牌 (策略1)
        token_type="bearer"
    )


# --- 12. 新增：更新当前用户信息端点 ---
@app.patch("/users/me", response_model=UserRead, tags=USERS_TAGS)  # USERS_TAGS 已在 /users/me (GET) 处定义
async def update_user_me(
        user_update_data: UserUpdate,  # <--- 2. 接收 UserUpdate 模型的数据
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)  # <--- 3. 获取当前登录用户
):
    """
    更新当前登录用户的个人资料。
    用户可以更新 full_name, bio, 和 avatar_url。
    """
    # 4. 将 Pydantic 模型转换为字典，但只包含用户实际设置的字段
    #    exclude_unset=True 确保了如果用户没有发送某个字段，我们不会用 None 覆盖它，除非用户显式发送了 null
    update_data = user_update_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供需要更新的数据"
        )

    updated_something = False
    for key, value in update_data.items():
        # 检查该字段是否是 User 模型中允许用户修改的字段
        if hasattr(current_user, key):
            setattr(current_user, key, value)
            updated_something = True

    if updated_something:
        current_user.updated_at = datetime.datetime.now(datetime.timezone.utc)  # 更新时间戳
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    else:
        # 如果 update_data 不为空，但所有字段都不是 User 模型的有效属性 (理论上不应该发生，因为 UserUpdate 字段有限)
        # 或者如果用户发送的数据与当前数据完全相同，这里也可以选择不执行 commit 和 refresh
        # 但由于 Pydantic 的 exclude_unset=True，如果发送的字段值与当前值相同，我们还是会尝试更新。
        # 如果希望仅在值实际更改时才更新 updated_at，则需要更复杂的比较逻辑。
        # 目前的逻辑是：只要用户在请求中提供了有效字段，就尝试更新并更新时间戳。
        pass

    return current_user


# --- 13. 新增：修改当前用户密码端点 ---
@app.post("/users/me/change-password", status_code=status.HTTP_200_OK, tags=USERS_TAGS)
async def change_current_user_password(
        password_update_data: UserPasswordUpdate,  # <--- 3. 接收 UserPasswordUpdate 模型的数据
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)  # <--- 4. 获取当前登录用户
):
    """
    修改当前登录用户的密码。
    需要提供当前密码和新密码（及确认）。
    """
    # 5. 验证当前密码是否正确
    if not verify_password(password_update_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 或者 401 Unauthorized，取决于你的错误处理偏好
            detail="当前密码不正确",
        )

    # 6. UserPasswordUpdate 模型中的 @model_validator 已经确保了 new_password 和 new_password_confirm 匹配
    #    并且 new_password 满足 min_length=8 的要求（在 Field 定义中）。

    # 7. 哈希新密码
    new_hashed_password = get_password_hash(password_update_data.new_password)

    # 8. 更新用户的哈希密码和 updated_at 时间戳
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.datetime.now(datetime.timezone.utc)

    session.add(current_user)
    session.commit()
    # session.refresh(current_user) # 通常在密码修改后不需要 refresh，因为我们不直接返回用户信息

    # （可选）在密码成功修改后，可以考虑使该用户的所有其他活动会话/刷新令牌失效。
    # 这需要更复杂的令牌吊销机制，目前我们不实现。

    return {"message": "密码已成功更新"}


# --- 14. 新增：请求密码重置端点 ---
@app.post("/auth/request-password-reset", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def request_password_reset(
        reset_request: PasswordResetRequest,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == reset_request.email)).first()

    if user:
        try:
            raw_reset_token = generate_password_reset_token(user.email)
            token_hash_for_db = get_password_hash(raw_reset_token)
            expires_delta = datetime.timedelta(seconds=settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS)
            token_expires_at = datetime.datetime.now(datetime.timezone.utc) + expires_delta

            password_reset_token_db = PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash_for_db,
                expires_at=token_expires_at
            )
            session.add(password_reset_token_db)
            session.commit()

            # --- 解除这部分注释并使用新的邮件函数 ---
            background_tasks.add_task(
                send_password_reset_email,  # <--- 使用新的函数名
                email_to=user.email,
                username=user.username,
                token=raw_reset_token
            )
            print(f"密码重置邮件任务已为 {user.email} 添加到后台队列。")
            # -----------------------------------------

        except Exception as e:
            print(f"为用户 {reset_request.email} 请求密码重置时发生内部错误: {e}")
            pass

    return {"message": "如果您的邮箱地址在我们系统中注册过，您将会收到一封包含密码重置说明的邮件。"}


# --- 15. 新增：重置密码端点 ---
@app.post("/auth/reset-password", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def reset_password(
        password_reset_form: PasswordResetForm,  # <--- 2. 接收包含令牌和新密码的请求体
        session: Session = Depends(get_session)
):
    """
    用户使用从邮件中获取的令牌来重置密码。
    """
    # 3. 验证密码重置令牌的有效性 (签名和有效期)
    email_from_token = verify_password_reset_token(password_reset_form.token)
    if not email_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的密码重置令牌",
        )

    # 4. 根据从令牌中获取的邮箱查找用户
    user = session.exec(select(User).where(User.email == email_from_token)).first()
    if not user:
        # 这种情况理论上不应该发生，因为令牌是基于已注册用户的邮箱生成的
        # 但作为安全措施，还是需要检查
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 或者 404，但 400 更符合“令牌无效”的语境
            detail="与此令牌关联的用户未找到",
        )

    if not user.is_active:
        # 不允许非活动用户重置密码
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用，无法重置密码",
        )

    # 5. PasswordResetForm 模型中的 @model_validator 已经确保了 new_password 和 new_password_confirm 匹配
    #    并且 new_password 满足 min_length=8 的要求。

    # 6. 哈希新密码
    new_hashed_password = get_password_hash(password_reset_form.new_password)

    # 7. 更新用户的哈希密码和 updated_at 时间戳
    user.hashed_password = new_hashed_password
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(user)

    # 8. 使已使用的密码重置令牌失效 (从数据库中删除)
    #    我们需要对传入的原始令牌进行哈希，以匹配数据库中存储的 token_hash。
    token_hash_to_lookup = get_password_hash(password_reset_form.token)
    db_token_record = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash_to_lookup)
    ).first()

    if db_token_record:
        # （可选但推荐）再次确认令牌属于同一个用户
        if db_token_record.user_id == user.id:
            session.delete(db_token_record)
        else:
            # 令牌哈希匹配但用户ID不匹配，这是异常情况，可能表示哈希碰撞或安全问题
            # 之前用户状态已改变，这里需要回滚
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码重置令牌与用户不匹配，操作失败",
            )
    else:
        # 如果在数据库中找不到对应的令牌哈希记录，
        # 但令牌本身（签名和时间）是有效的，这可能是个问题。
        # 可能是令牌已被使用过并删除，或者存储时出了问题。
        # 为安全起见，如果严格要求DB中有对应记录才能验证，这里应报错并回滚。
        print(f"警告: 有效的签名令牌，但在数据库中未找到对应的密码重置令牌哈希记录。邮箱: {email_from_token}")
        # 如果需要严格检查，则取消下面两行注释:
        # session.rollback()
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码重置令牌记录未找到或已使用")
        pass  # 当前选择：如果签名令牌有效，即使DB无记录也允许通过（但留有警告）

    session.commit()  # 提交用户密码更新和令牌删除

    return {"message": "密码已成功重置，您现在可以使用新密码登录。"}


# --- 2. 新增：缩略图生成函数 ---
def create_thumbnail(
        original_image_path: Path,
        thumbnail_save_path: Path,
        size: tuple[int, int] = (200, 200)  # 默认缩略图大小
):
    """
    使用 Pillow 生成图片的缩略图。
    """
    try:
        img = PILImage.open(original_image_path)
        # 对于 Pillow 9.1.0+，使用 Resampling.LANCZOS
        # 对于旧版本，使用 PILImage.ANTIALIAS
        # 我们假设使用的是较新版本
        img.thumbnail(size, Resampling.LANCZOS)  # [cite: 54]
        img.save(thumbnail_save_path)
        print(f"缩略图已保存到: {thumbnail_save_path}")
        return True
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return False


# --- 10. 新增：文件上传端点 ---
@app.post("/gallery/upload", response_model=GalleryItemReadWithUploader, status_code=status.HTTP_201_CREATED,
          tags=GALLERY_TAGS)
async def upload_gallery_item(
        title: str = File(...),
        description: Optional[str] = File(None),
        image: UploadFile = File(...),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    # --- 文件验证 (保持不变) ---
    allowed_mime_types = ["image/jpeg", "image/png", "image/gif"]
    if image.content_type not in allowed_mime_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {image.content_type}.")
    max_file_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_file_size:  # [cite: 50]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"文件过大，最大允许 {max_file_size // (1024 * 1024)}MB.")

    # --- 文件名处理 (保持不变) ---
    file_extension = Path(image.filename).suffix.lower()
    if not file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
        # 根据MIME类型更安全地决定扩展名
        if image.content_type == "image/jpeg":
            file_extension = ".jpg"
        elif image.content_type == "image/png":
            file_extension = ".png"
        elif image.content_type == "image/gif":
            file_extension = ".gif"
        else:
            file_extension = ".jpg"  # 默认

    unique_filename_base = str(uuid.uuid4())  # [cite: 52]
    original_filename = f"{unique_filename_base}{file_extension}"
    thumbnail_filename = f"{unique_filename_base}_thumb{file_extension}"

    original_file_location = UPLOAD_DIR / original_filename
    thumbnail_file_location = UPLOAD_DIR / thumbnail_filename

    # --- 保存原始文件 (保持不变) ---
    try:
        with open(original_file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
    except Exception as e:
        print(f"保存文件失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件时发生服务器内部错误。")
    finally:
        image.file.close()

    # --- 3. 生成缩略图 ---
    thumbnail_url_to_store = None
    if create_thumbnail(original_file_location, thumbnail_file_location):
        # 假设缩略图也通过 /uploads/ 路径提供服务
        thumbnail_url_to_store = f"/uploads/{thumbnail_filename}"

        # --- 创建数据库记录 (更新 image_url 和 thumbnail_url) ---
    image_url_to_store = f"/uploads/{original_filename}"  # <--- 3. 更新原始图片 URL

    gallery_item_data = GalleryItemCreate(
        title=title,
        description=description,
        image_url=image_url_to_store,  # 现在是相对 URL 路径
        thumbnail_url=thumbnail_url_to_store  # 现在是相对 URL 路径 (如果成功生成)
    )

    db_gallery_item = GalleryItem(
        **gallery_item_data.model_dump(),
        user_id=current_user.id,
    )

    session.add(db_gallery_item)
    session.commit()
    session.refresh(db_gallery_item)

    return db_gallery_item

# --- 11. 新增：获取画廊项目列表端点 (支持分页) ---
class PaginatedGalleryItems(SQLModel): # <--- 3. 定义分页响应模型
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GalleryItemReadWithUploader]

@app.get("/gallery/items", response_model=PaginatedGalleryItems, tags=GALLERY_TAGS)
async def get_gallery_items(
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1, description="页码，从1开始"), # <--- 4. 分页参数
    page_size: int = Query(10, ge=1, le=100, description="每页项目数量") # <--- 4. 分页参数
):
    """
    获取画廊项目列表，支持分页。
    默认按上传时间降序排列。
    """
    offset = (page - 1) * page_size

    # 5. 构建查询以获取当前页的项目
    #    我们希望同时获取上传者信息，SQLModel 的 Relationship 和 Pydantic 序列化通常会自动处理
    #    但为了确保 N+1 问题得到优化，可以考虑使用 selectinload (需要异步会话和更复杂的查询)
    #    对于同步会话，SQLModel 的关系加载通常在访问属性时发生，或在序列化时智能加载。

    # 先获取总项目数用于分页计算
    total_items_statement = select(func.count(GalleryItem.id))
    total_items = session.exec(total_items_statement).one() #

    if total_items == 0:
        return PaginatedGalleryItems(
            total_items=0,
            total_pages=0,
            page=page,
            page_size=page_size,
            items=[]
        )

    statement = (
        select(GalleryItem)
        .order_by(GalleryItem.uploaded_at.desc()) # 按上传时间降序
        .offset(offset)
        .limit(page_size)
    )
    gallery_items_db = session.exec(statement).all()

    # 手动构建嵌套的 uploader 信息 (如果 SQLModel/Pydantic 自动处理不符合预期)
    # results_with_uploader = []
    # for item in gallery_items_db:
    #     uploader_info = None
    #     if item.uploader: # 访问 uploader 属性会触发加载 (如果配置正确)
    #         uploader_info = UserRead.model_validate(item.uploader) # 将 User ORM 对象转为 UserRead Pydantic 模型
    #     results_with_uploader.append(
    #         GalleryItemReadWithUploader(
    #             **item.model_dump(), # 转换 GalleryItem 为字典
    #             uploader=uploader_info
    #         )
    #     )
    #
    # 然而，SQLModel 和 Pydantic v2 通常能很好地处理嵌套模型的序列化，
    # 只要 GalleryItemReadWithUploader.uploader 字段的类型提示是 UserRead，
    # 并且 GalleryItem.uploader 关系已正确定义。

    total_pages = (total_items + page_size - 1) // page_size # 计算总页数

    return PaginatedGalleryItems(
        total_items=total_items,
        total_pages=total_pages,
        page=page,
        page_size=page_size,
        items=gallery_items_db # 直接传递 ORM 对象列表，Pydantic 会处理序列化
    )


# --- 用于直接运行 Uvicorn (主要用于开发) ---
if __name__ == "__main__":
    print(f"启动 Uvicorn 开发服务器，API 地址: http://localhost:8000")
    print(f"允许的前端源 (CORS): {origins}")
    uvicorn.run(
        "main:app",  # 指向 FastAPI 应用实例
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,
        reload=False,  # 开启自动重载
        log_level="info"
    )
