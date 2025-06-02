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
import datetime
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func  # 确保导入
from sqlmodel import Session, select, SQLModel  # 确保导入 SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# 项目内部模块导入
# 假设所有这些文件都在 backend 目录或其子目录中，并且 Python 的导入路径能正确解析
from backend.database import get_session, get_async_session  # create_db_and_tables 不再需要从这里导入
from backend.models import (
    User,
    UserCreate,
    UserRead,
    VerificationToken,  # 用于邮件验证和密码重置中的令牌删除逻辑
    PasswordResetToken,  # 用于密码重置逻辑
    Token,
    RefreshTokenRequest,
    UserPasswordUpdate,
    UserUpdate,
    PasswordResetRequest,
    PasswordResetForm,
    GalleryItemCreate,
    GalleryItem,
    GalleryItemReadWithUploader  # 用于画廊API响应
)
from backend.auth_utils import (
    get_password_hash,
    generate_email_verification_token,
    verify_email_verification_token,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_refresh_token_and_get_token_data,
    generate_password_reset_token,  # 已在 auth_utils.py 中
    verify_password_reset_token  # 已在 auth_utils.py 中
)
from backend.email_utils import send_verification_email, send_password_reset_email
from backend.core.config import settings
from PIL import Image as PILImage
from PIL.Image import Resampling
import io

# --- 上传文件存储目录定义 ---
UPLOAD_DIR = Path(__file__).parent / "uploads"  # 将目录放在 backend 文件夹内
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --- FastAPI 应用生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用启动中...")
    # create_db_and_tables() # 已移至 create_tables.py
    print("数据库表结构应由 create_tables.py 脚本创建。")
    yield
    print("应用关闭中...")


app = FastAPI(
    title=settings.MAIL_FROM_NAME + " API",  # 使用配置中的名称
    version="0.1.0",
    lifespan=lifespan
)

# --- CORS 中间件设置 ---
configured_origins = [
    settings.PORTAL_FRONTEND_BASE_URL,
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:63342",  # 根据您之前的反馈添加
]
allow_origins_list = list(set(o for o in configured_origins if o))
if not allow_origins_list:
    allow_origins_list = ["http://localhost:5173"]  # 默认值

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 静态文件服务 ---
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- 根路径 ---
@app.get("/", tags=["General"])
async def read_root():
    return {"message": f"欢迎来到 {settings.MAIL_FROM_NAME} API"}


# --- 认证相关端点 ---
AUTH_TAGS = ["Authentication"]


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=AUTH_TAGS)
async def register_user(
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    existing_user_by_username = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()
    if existing_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户名已被使用")

    existing_user_by_email = session.exec(
        select(User).where(User.email == user_create.email)
    ).first()
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册")

    hashed_password = get_password_hash(user_create.password)
    db_user = User.model_validate(user_create,
                                  update={"hashed_password": hashed_password, "is_verified": False, "is_active": True})
    # db_user = User(
    #     username=user_create.username,
    #     email=user_create.email,
    #     hashed_password=hashed_password,
    #     full_name=user_create.full_name,
    #     bio=user_create.bio,
    #     avatar_url=user_create.avatar_url,
    #     is_active=True,
    #     is_verified=False,
    # )
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
    except Exception as e:
        print(f"创建用户 {db_user.username} 后，处理邮件验证时发生错误: {e}")
        pass
    return db_user


@app.get("/auth/verify-email", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def verify_email_address(
        token: str,
        session: Session = Depends(get_session)
):
    email_from_token = verify_email_verification_token(token)
    if not email_from_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效或已过期的验证令牌")

    user = session.exec(select(User).where(User.email == email_from_token)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="与此令牌关联的用户未找到")

    if user.is_verified:
        return {"message": "邮箱已成功验证"}

    user.is_verified = True
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(user)

    token_hash_to_lookup = get_password_hash(token)
    db_token_record = session.exec(
        select(VerificationToken).where(VerificationToken.token_hash == token_hash_to_lookup)
    ).first()

    if db_token_record:
        if db_token_record.user_id == user.id:
            session.delete(db_token_record)
        else:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证令牌与用户不匹配，验证失败")
    else:
        print(f"警告: 有效的签名令牌，但在数据库中未找到对应的验证令牌哈希记录。邮箱: {email_from_token}")
        # 根据业务需求决定是否依然验证。当前选择：允许。

    session.commit()
    session.refresh(user)
    return {"message": "邮箱验证成功！您现在可以登录了。"}


@app.post("/auth/token", response_model=Token, tags=AUTH_TAGS)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用，请联系管理员")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱未验证，请先验证您的邮箱")

    token_data_payload = {"sub_id": user.id}
    access_token = create_access_token(data=token_data_payload)
    refresh_token = create_refresh_token(data=token_data_payload)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@app.post("/auth/refresh-token", response_model=Token, tags=AUTH_TAGS)
async def refresh_access_token(
        refresh_request: RefreshTokenRequest,
        session: Session = Depends(get_session)
):
    refresh_token_str = refresh_request.refresh_token
    token_data = verify_refresh_token_and_get_token_data(refresh_token_str)
    if not token_data or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = session.get(User, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="与此刷新令牌关联的用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用")

    new_access_token_payload = {"sub_id": user.id}
    new_access_token = create_access_token(data=new_access_token_payload)
    return Token(access_token=new_access_token, refresh_token=refresh_token_str, token_type="bearer")


@app.post("/auth/request-password-reset", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def request_password_reset(
        reset_request: PasswordResetRequest,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == reset_request.email)).first()
    if user:  # 只在用户存在时发送邮件
        try:
            raw_reset_token = generate_password_reset_token(user.email)
            token_hash_for_db = get_password_hash(raw_reset_token)
            expires_delta = datetime.timedelta(seconds=settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS)
            token_expires_at = datetime.datetime.now(datetime.timezone.utc) + expires_delta

            # 删除该用户已有的密码重置令牌
            existing_tokens = session.exec(
                select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)).all()
            for t in existing_tokens:
                session.delete(t)

            password_reset_token_db = PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash_for_db,
                expires_at=token_expires_at
            )
            session.add(password_reset_token_db)
            session.commit()

            background_tasks.add_task(
                send_password_reset_email,
                email_to=user.email,
                username=user.username,
                token=raw_reset_token
            )
        except Exception as e:
            print(f"为用户 {reset_request.email} 请求密码重置时发生内部错误: {e}")
            pass
    return {"message": "如果您的邮箱地址在我们系统中注册过，您将会收到一封包含密码重置说明的邮件。"}


@app.post("/auth/reset-password", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def reset_password(
        password_reset_form: PasswordResetForm,
        session: Session = Depends(get_session)
):
    email_from_token = verify_password_reset_token(password_reset_form.token)
    if not email_from_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效或已过期的密码重置令牌")

    user = session.exec(select(User).where(User.email == email_from_token)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="与此令牌关联的用户未找到")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户账户已被禁用，无法重置密码")

    new_hashed_password = get_password_hash(password_reset_form.new_password)
    user.hashed_password = new_hashed_password
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(user)

    token_hash_to_lookup = get_password_hash(password_reset_form.token)
    db_token_record = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash_to_lookup)
    ).first()

    if db_token_record:
        if db_token_record.user_id == user.id:
            session.delete(db_token_record)
        else:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码重置令牌与用户不匹配，操作失败")
    else:
        # 如果令牌本身有效，但DB中无记录，可能已被使用。出于安全，通常应报错。
        session.rollback()  # 回滚对 user 对象的任何未提交更改（如密码更新）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码重置令牌记录未找到或可能已被使用。请重新请求密码重置。"
        )

    try:
        session.commit()
        # session.refresh(user) # refresh user 不是必须的，因为我们只返回消息
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新密码或提交事务时发生内部错误: {e}"  # 细化错误信息
        )
    return {"message": "密码已成功重置，您现在可以使用新密码登录。"}

# --- 用户信息管理端点 ---
USERS_TAGS = ["Users"]


@app.get("/users/me", response_model=UserRead, tags=USERS_TAGS)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.patch("/users/me", response_model=UserRead, tags=USERS_TAGS)
async def update_user_me(
        user_update_data: UserUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    update_data = user_update_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供需要更新的数据")

    updated_something = False
    for key, value in update_data.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)
            updated_something = True

    if updated_something:
        current_user.updated_at = datetime.datetime.now(datetime.timezone.utc)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    return current_user


@app.post("/users/me/change-password", status_code=status.HTTP_200_OK, tags=USERS_TAGS)
async def change_current_user_password(
        password_update_data: UserPasswordUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    if not verify_password(password_update_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")

    new_hashed_password = get_password_hash(password_update_data.new_password)
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(current_user)
    session.commit()
    return {"message": "密码已成功更新"}


# --- 画廊功能端点 ---
GALLERY_TAGS = ["Gallery"]


def create_thumbnail(
        original_image_path: Path,
        thumbnail_save_path: Path,
        size: tuple[int, int] = (200, 200)
):
    try:
        img = PILImage.open(original_image_path)
        img.thumbnail(size, Resampling.LANCZOS)
        img.save(thumbnail_save_path)
        print(f"缩略图已保存到: {thumbnail_save_path}")
        return True
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return False


@app.post("/gallery/upload", response_model=GalleryItemReadWithUploader, status_code=status.HTTP_201_CREATED,
          tags=GALLERY_TAGS)
async def upload_gallery_item(
        title: str = File(...),
        description: Optional[str] = File(None),
        image: UploadFile = File(...),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_active_user)
):
    allowed_mime_types = ["image/jpeg", "image/png", "image/gif"]
    if image.content_type not in allowed_mime_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {image.content_type}.")

    MAX_FILE_SIZE_MB = 5
    max_file_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if image.size > max_file_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"文件过大，最大允许 {MAX_FILE_SIZE_MB}MB.")

    file_extension = Path(image.filename).suffix.lower()
    if not file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
        mime_to_ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif"}
        file_extension = mime_to_ext.get(image.content_type, ".jpg")  # 默认 .jpg

    unique_filename_base = str(uuid.uuid4())
    original_filename = f"{unique_filename_base}{file_extension}"
    thumbnail_filename = f"{unique_filename_base}_thumb{file_extension}"

    original_file_location = UPLOAD_DIR / original_filename
    thumbnail_file_location = UPLOAD_DIR / thumbnail_filename

    try:
        with open(original_file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
    except Exception as e:
        print(f"保存文件失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件时发生服务器内部错误。")
    finally:
        image.file.close()

    thumbnail_url_to_store = None
    if create_thumbnail(original_file_location, thumbnail_file_location):
        thumbnail_url_to_store = f"/uploads/{thumbnail_filename}"

    image_url_to_store = f"/uploads/{original_filename}"

    gallery_item_create_data = GalleryItemCreate(
        title=title,
        description=description,
        image_url=image_url_to_store,
        thumbnail_url=thumbnail_url_to_store
    )
    db_gallery_item = GalleryItem.model_validate(gallery_item_create_data, update={"user_id": current_user.id})
    # db_gallery_item = GalleryItem(
    #     **gallery_item_create_data.model_dump(),
    #     user_id=current_user.id,
    # )
    session.add(db_gallery_item)
    session.commit()
    session.refresh(db_gallery_item)
    return db_gallery_item


class PaginatedGalleryItems(SQLModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GalleryItemReadWithUploader]


@app.get("/gallery/items", response_model=PaginatedGalleryItems, tags=GALLERY_TAGS)
async def get_gallery_items(
        session: AsyncSession = Depends(get_async_session),  # 假设您现在是同步操作，如果是异步，应该是 AsyncSession 和 get_async_session
        page: int = Query(1, ge=1, description="页码，从1开始"),
        page_size: int = Query(10, ge=1, le=100, description="每页项目数量")
):
    offset = (page - 1) * page_size

    # 之前用于调试的打印语句可以保留或移除
    # print(f"--- DEBUG INFO ---")
    # print(f"SQLModel version being used: {sqlmodel.__version__}")
    # print(f"Type of 'session' object: {type(session)}")
    # print(f"Is 'session' an instance of SQLModelSession? {isinstance(session, sqlmodel.Session)}") # 使用 sqlmodel.Session
    # print(f"Is 'session' an instance of SQLAlchemySession? {isinstance(session, SQLAlchemySession)}") # 需要从 sqlalchemy.orm import Session as SQLAlchemySession
    # print(f"Attributes of 'session': {dir(session)}")
    # print(f"--- END DEBUG INFO ---")

    total_items_statement = select(func.count(GalleryItem.id))

    # session.exec() 返回一个 Result 对象。对于 count() 这样的聚合函数，
    # 我们期望得到一个标量值。
    total_items = (await session.exec(total_items_statement)).one_or_none()


    total_items = total_items if total_items is not None else 0

    if total_items == 0:
        return PaginatedGalleryItems(total_items=0, total_pages=0, page=page, page_size=page_size, items=[])

    statement = (
        select(GalleryItem)
        .order_by(GalleryItem.uploaded_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    # session.exec() 返回 Result 对象，然后我们可以用 .all() 获取所有 ORM 实例
    results_for_items =  await session.exec(statement)
    gallery_items_db = results_for_items.all()

    total_pages = (total_items + page_size - 1) // page_size

    return PaginatedGalleryItems(
        total_items=total_items,
        total_pages=total_pages,
        page=page,
        page_size=page_size,
        items=gallery_items_db
    )


# --- 用于直接运行 Uvicorn (主要用于开发) ---
if __name__ == "__main__":
    print(f"启动 Uvicorn 开发服务器，API 地址: http://127.0.0.1:8000")
    print(f"允许的前端源 (CORS): {allow_origins_list}")  # 使用已定义的 allow_origins_list
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 建议在调试启动问题时先设为 False
        log_level="info"
    )