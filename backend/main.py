# backend/main.py
import datetime
import logging
import shutil
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List

import httpx
import uvicorn
from PIL import Image as PILImage
from PIL.Image import Resampling
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqladmin import Admin
from sqlmodel import SQLModel  # 确保导入 SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import StreamingResponse

from backend import crud
from backend.admin import admin_views
from backend.admin_auth import authentication_backend
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
    verify_password_reset_token, get_current_admin_user  # 已在 auth_utils.py 中
)
from backend.core.config import settings
from backend.crud import get_friend_links
# 项目内部模块导入
# 假设所有这些文件都在 backend 目录或其子目录中，并且 Python 的导入路径能正确解析
from backend.database import get_async_session, sync_engine  # create_db_and_tables 不再需要从这里导入
from backend.email_utils import send_verification_email, send_password_reset_email
from backend.models import (
    User,
    UserCreate,
    UserRead,
    # 用于邮件验证和密码重置中的令牌删除逻辑
    # 用于密码重置逻辑
    Token,
    RefreshTokenRequest,
    UserPasswordUpdate,
    UserUpdate,
    PasswordResetRequest,
    PasswordResetForm,
    GalleryItemCreate,
    # 你可能需要创建一个用于更新的模型
    GalleryItemReadWithBuilder, Member, MemberRead, MemberCreate, MemberUpdate, FriendLinkRead  # 使用新的响应模型
)

# --- 上传文件存储目录定义 ---
UPLOAD_DIR = Path(__file__).parent / "uploads"  # 将目录放在 backend 文件夹内
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # 输出到控制台
        # 如果需要，可以添加输出到文件的 Handler
        # logging.FileHandler("app.log")
    ]
)
# 获取一个日志记录器实例
logger = logging.getLogger(__name__)


# --- FastAPI 应用生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")
    yield
    logger.info("应用关闭中...")


app = FastAPI(
    title=settings.MAIL_FROM_NAME + " API",  # 使用配置中的名称
    version="0.1.0",
    lifespan=lifespan
)


class PublicConfig(BaseModel):
    enable_registration: bool
    project_name: str

# --- Admin Panel Setup ---
admin = Admin(app, sync_engine, authentication_backend=authentication_backend)

# 注册所有视图
for view in admin_views:
    admin.add_view(view)

# --- CORS 中间件设置 ---
configured_origins = [
    settings.PORTAL_FRONTEND_BASE_URL,
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
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


@app.get("/config/public", response_model=PublicConfig, tags=["Public"])
async def get_public_config():
    """获取前端需要的、公开的后端配置信息。"""
    return PublicConfig(
        enable_registration=settings.ENABLE_REGISTRATION,
        project_name=settings.MAIL_FROM_NAME
    )

# --- 新增：Minecraft 头像代理接口 ---
# 把它放在其他路由定义之前
@app.get("/avatars/mc/{username}", tags=["Public"])
async def get_mc_avatar(username: str):
    """
    一个代理接口，用于从 cravatar.eu 获取 Minecraft 头像，以避免客户端跨域或网络问题。
    """
    avatar_url = f"https://cravatar.eu/avatar/{username}/128.png"
    async with httpx.AsyncClient() as client:
        try:
            # 使用流式请求，提高效率
            req = client.build_request("GET", avatar_url, timeout=10.0)
            r = await client.send(req, stream=True)
            r.raise_for_status()  # 如果请求失败 (如 404), 则会抛出异常

            # 将 cravatar 的响应头和内容流式传输给客户端
            return StreamingResponse(r.aiter_bytes(), headers=r.headers)

        except httpx.HTTPStatusError as e:
            # 如果 cravatar 返回 404 (用户不存在), 则也返回 404
            raise HTTPException(status_code=e.response.status_code, detail="Avatar not found.")
        except Exception as e:
            # 其他网络错误
            raise HTTPException(status_code=502, detail=f"Could not fetch avatar from upstream server: {e}")


# --- 认证相关端点 ---
AUTH_TAGS = ["Authentication"]

@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=AUTH_TAGS)
async def register_user(
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session)
):
    if not settings.ENABLE_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户注册功能当前已关闭"
        )


    if await crud.get_user_by_email(db=session, email=user_create.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册")
    if await crud.get_user_by_username(db=session, username=user_create.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户名已被使用")
    if user_create.mc_name and await crud.get_user_by_mc_name(db=session, mc_name=user_create.mc_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该 Minecraft 用户名已被关联")

    db_user = await crud.create_user(db=session, user_create=user_create)

    try:
        raw_token = generate_email_verification_token(db_user.email)
        await crud.create_verification_token(
            db=session,
            user_id=db_user.id,
            token_hash=get_password_hash(raw_token),
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=settings.EMAIL_TOKEN_MAX_AGE_SECONDS)
        )
        background_tasks.add_task(send_verification_email, email_to=db_user.email, username=db_user.username, token=raw_token)
    except Exception as e:
        logger.error(f"创建用户 {db_user.username} 后，处理邮件验证时发生错误: {e}")

    return db_user


@app.get("/auth/verify-email", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def verify_email_address(token: str, session: AsyncSession = Depends(get_async_session)):
    email = verify_email_verification_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效或已过期的验证令牌")

    user = await crud.get_user_by_email(db=session, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="与此令牌关联的用户未找到")
    if user.is_verified:
        return {"message": "邮箱已成功验证"}

    user.is_verified = True
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    await session.commit()
    await session.refresh(user)

    db_token = await crud.get_verification_token_by_hash(db=session, token_hash=get_password_hash(token))
    if db_token:
        await crud.delete_db_token(db=session, token=db_token)

    return {"message": "邮箱验证成功！您现在可以登录了。"}


@app.post("/auth/token", response_model=Token, tags=AUTH_TAGS)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    user = await crud.get_user_by_email(db=session, email=form_data.username)
    if not user:
        user = await crud.get_user_by_username(db=session, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱/用户名或密码不正确")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已被禁用")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱未验证")

    return Token(
        access_token=create_access_token({"sub_id": user.id}),
        refresh_token=create_refresh_token({"sub_id": user.id}),
        token_type="bearer"
    )


@app.post("/auth/refresh-token", response_model=Token, tags=AUTH_TAGS)
async def refresh_access_token(refresh_request: RefreshTokenRequest,
                               session: AsyncSession = Depends(get_async_session)):
    token_data = verify_refresh_token_and_get_token_data(refresh_request.refresh_token)
    if not token_data or not token_data.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效或已过期的刷新令牌")

    user = await crud.get_user_by_id(db=session, user_id=token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")

    return Token(
        access_token=create_access_token({"sub_id": user.id}),
        refresh_token=refresh_request.refresh_token,
        token_type="bearer"
    )


@app.post("/auth/request-password-reset", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def request_password_reset(reset_request: PasswordResetRequest, background_tasks: BackgroundTasks,
                                 session: AsyncSession = Depends(get_async_session)):
    user = await crud.get_user_by_email(db=session, email=reset_request.email)
    if user:
        try:
            raw_token = generate_password_reset_token(user.email)
            await crud.create_password_reset_token(
                db=session,
                user_id=user.id,
                token_hash=get_password_hash(raw_token),
                expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                    seconds=settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS)
            )
            background_tasks.add_task(send_password_reset_email, email_to=user.email, username=user.username,
                                      token=raw_token)
        except Exception as e:
            logger.error(f"为用户 {reset_request.email} 请求密码重置时发生内部错误: {e}")

    return {"message": "如果您的邮箱地址在我们系统中注册过，您将会收到一封包含密码重置说明的邮件。"}



@app.post("/auth/reset-password", status_code=status.HTTP_200_OK, tags=AUTH_TAGS)
async def reset_password(form: PasswordResetForm, session: AsyncSession = Depends(get_async_session)):
    email = verify_password_reset_token(form.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效或已过期的密码重置令牌")

    user = await crud.get_user_by_email(db=session, email=email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在或已被禁用")

    db_token = await crud.get_password_reset_token_by_hash(db=session, token_hash=get_password_hash(form.token))
    if not db_token or db_token.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码重置令牌无效或已被使用")

    await crud.update_user_password(db=session, user=user, new_password=form.new_password)
    await crud.delete_db_token(db=session, token=db_token)

    return {"message": "密码已成功重置。"}



# --- 用户信息管理端点 ---
USERS_TAGS = ["Users"]


@app.get("/users/me", response_model=UserRead, tags=USERS_TAGS)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.patch("/users/me", response_model=UserRead, tags=USERS_TAGS)
async def update_user_me(user_update: UserUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    if not user_update.model_dump(exclude_unset=True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供需要更新的数据")
    if user_update.mc_name and user_update.mc_name != current_user.mc_name:
        existing_user = await crud.get_user_by_mc_name(db=session, mc_name=user_update.mc_name)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该 Minecraft 用户名已被其他用户关联")


    return await crud.update_user(db=session, user=current_user, user_update=user_update)



@app.post("/users/me/change-password", status_code=status.HTTP_200_OK, tags=USERS_TAGS)
async def change_current_user_password(password_update: UserPasswordUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")
    await crud.update_user_password(db=session, user=current_user, new_password=password_update.new_password)
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
        logger.info(f"缩略图已保存到: {thumbnail_save_path}")
        return True
    except Exception as e:
        logger.error(f"创建缩略图失败: {e}")
        return False


@app.post("/gallery/upload", response_model=GalleryItemReadWithBuilder, status_code=status.HTTP_201_CREATED, tags=GALLERY_TAGS)
async def upload_gallery_item(
        title: str = File(...),
        builder_name: str = File(...),
        description: Optional[str] = File(None),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_active_user)
):
    # 步骤 1: 文件验证 (来自原始代码)
    allowed_mime_types = ["image/jpeg", "image/png", "image/gif"]
    if image.content_type not in allowed_mime_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"不支持的文件类型: {image.content_type}.")

    MAX_FILE_SIZE_MB = 5
    max_file_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if image.size > max_file_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"文件过大，最大允许 {MAX_FILE_SIZE_MB}MB.")

    # 步骤 2: 生成唯一文件名 (来自原始代码)
    file_extension = Path(image.filename).suffix.lower()
    if not file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
        mime_to_ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif"}
        file_extension = mime_to_ext.get(image.content_type, ".jpg")

    unique_filename_base = str(uuid.uuid4())
    original_filename = f"{unique_filename_base}{file_extension}"
    thumbnail_filename = f"{unique_filename_base}_thumb{file_extension}"

    original_file_location = UPLOAD_DIR / original_filename
    thumbnail_file_location = UPLOAD_DIR / thumbnail_filename

    # 步骤 3: 从数据库获取或创建成员 (调用 CRUD)
    member = await crud.get_or_create_member(db=session, name=builder_name)

    # 步骤 4: 保存上传的原始文件到本地 (来自原始代码)
    try:
        with open(original_file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传文件时发生服务器内部错误。")
    finally:
        image.file.close()

    # 步骤 5: 创建缩略图 (来自原始代码)
    thumbnail_url_to_store = None
    if create_thumbnail(original_file_location, thumbnail_file_location):
        thumbnail_url_to_store = f"/uploads/{thumbnail_filename}"

    image_url_to_store = f"/uploads/{original_filename}"

    # 步骤 6: 准备数据并通过 CRUD 函数写入数据库
    item_create_data = GalleryItemCreate(
        title=title,
        description=description,
        image_url=image_url_to_store,
        thumbnail_url=thumbnail_url_to_store
    )

    db_gallery_item = await crud.create_gallery_item(
        db=session,
        item_create=item_create_data,
        user_id=current_user.id,
        member_id=member.id
    )

    return db_gallery_item


class PaginatedGalleryItems(SQLModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GalleryItemReadWithBuilder]


@app.get("/gallery/items", response_model=PaginatedGalleryItems, tags=GALLERY_TAGS)
async def get_gallery_items(session: AsyncSession = Depends(get_async_session), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    total_items, items = await crud.get_paginated_gallery_items(db=session, page=page, page_size=page_size)
    total_pages = (total_items + page_size - 1) // page_size
    return PaginatedGalleryItems(total_items=total_items, total_pages=total_pages, page=page, page_size=page_size, items=items)



# --- 新增：画廊项目管理端点 (更新和删除) ---
class GalleryItemUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    # 可以添加修改 builder 的逻辑
    # builder_name: Optional[str] = None


@app.patch("/gallery/items/{item_id}", response_model=GalleryItemReadWithBuilder, tags=GALLERY_TAGS)
async def update_gallery_item(item_id: int, item_update: GalleryItemUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    db_item = await crud.get_gallery_item_by_id(db=session, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目未找到")
    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此项目")
    return await crud.update_gallery_item(db=session, item=db_item, item_update=item_update)



@app.delete("/gallery/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=GALLERY_TAGS)
async def delete_gallery_item(item_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    db_item = await crud.get_gallery_item_by_id(db=session, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目未找到")
    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此项目")
    await crud.delete_gallery_item(db=session, item=db_item)
    return


# --- 新增：成员管理端点 ---
MEMBERS_TAGS = ["Members"]


@app.post("/members", response_model=MemberRead, tags=MEMBERS_TAGS, status_code=status.HTTP_201_CREATED)
async def create_member(member_data: MemberCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    if await crud.get_member_by_name(db=session, name=member_data.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该名称的成员已存在")
    # In a real app, you might want to move model_validate into the crud function
    db_member = Member.model_validate(member_data)
    session.add(db_member)
    await session.commit()
    await session.refresh(db_member)
    return db_member


@app.get("/members", response_model=List[MemberRead], tags=MEMBERS_TAGS)
async def get_all_members(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_members(db=session)


@app.patch("/members/{member_id}", response_model=MemberRead, tags=MEMBERS_TAGS)
async def update_member(member_id: int, member_update: MemberUpdate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_active_user)):
    db_member = await crud.get_member_by_id(db=session, member_id=member_id)
    if not db_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员未找到")
    return await crud.update_member(db=session, member=db_member, member_update=member_update)



@app.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT, tags=MEMBERS_TAGS)
async def delete_member(
        member_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin_user: User = Depends(get_current_admin_user)
):
    db_member = await crud.get_member_by_id(db=session, member_id=member_id)
    if not db_member:
        # 细节：即使是管理员，也应该告诉他资源不存在
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员未找到")

    await crud.delete_member(db=session, member=db_member)
    return


@app.get("/friend-links", response_model=list[FriendLinkRead], tags=["Public"])
async def read_friend_links(db: AsyncSession = Depends(get_async_session)):
    """
    获取所有公开的友情链接列表
    """
    links = await get_friend_links(db)
    return links

# --- 用于直接运行 Uvicorn (主要用于开发) ---
if __name__ == "__main__":
    logger.info(f"启动 Uvicorn 开发服务器，API 地址: http://127.0.0.1:8000")
    logger.info(f"允许的前端源 (CORS): {allow_origins_list}")  # 使用已定义的 allow_origins_list
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 建议在调试启动问题时先设为 False
        log_level="info"
    )