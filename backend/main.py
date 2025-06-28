# backend/main.py
import datetime
import logging
import shutil
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List  # 导入 Union 用于文件类型提示
import json
from fastapi import Request
import cv2
import httpx
import uvicorn
from PIL import Image as PILImage
from PIL.Image import Resampling
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, select, desc  # 确保导入 SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import StreamingResponse

from backend import crud, models
from backend.auth_utils import (
    get_password_hash,
    generate_email_verification_token,
    verify_email_verification_token,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_refresh_token_and_get_token_data,
    generate_password_reset_token,
    verify_password_reset_token, get_current_admin_user
)
from backend.core.config import get_settings, clear_settings_cache, Settings
from backend.crud import get_friend_links
from backend.database import get_async_session
from backend.email_utils import send_verification_email, send_password_reset_email, send_account_deletion_email
from backend.models import (
    User,
    UserCreate,
    UserRead,
    Token,
    RefreshTokenRequest,
    UserPasswordUpdate,
    UserUpdate,
    PasswordResetRequest,
    PasswordResetForm,
    GalleryItemCreate,
    GalleryItemReadWithBuilder, MemberRead, MemberCreate, MemberUpdate, FriendLinkRead, ItemType, UserRole
)

# --- 上传文件存储目录定义 ---
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- 更健壮的路径定义 ---
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_DIR = PROJECT_ROOT / "backend/uploads"
SITE_CONFIG_PATH = PROJECT_ROOT / "frontend/public/site-config.json"

# --- FastAPI 应用生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")
    yield
    logger.info("应用关闭中...")


app = FastAPI(
    title=get_settings().MAIL_FROM_NAME + " API",
    version="0.1.0",
    lifespan=lifespan
)


class PublicConfig(BaseModel):
    enable_registration: bool
    project_name: str


# --- CORS 中间件设置 (在应用启动时读取一次配置) ---
initial_settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=initial_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware, secret_key=get_settings().SESSION_SECRET_KEY
)


# --- 静态文件服务 ---
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- 配置重载端点 ---
@app.post("/admin/reload-config", status_code=status.HTTP_200_OK, tags=["Admin"])
async def reload_configuration(admin_user: User = Depends(get_current_admin_user)):
    """
    (需要管理员权限)
    清除服务器端的配置缓存，使服务器从 .env 文件重新加载配置。
    注意：CORS等中间件配置在服务启动时加载，无法通过此方式热重载。
    """
    clear_settings_cache()
    return {"message": "配置已重载."}


# --- 根路径 ---
@app.get("/", tags=["General"])
async def read_root():
    return {"message": f"欢迎来到 {get_settings().MAIL_FROM_NAME} API!"}


@app.get("/config/public", response_model=PublicConfig, tags=["Public"])
async def get_public_config(settings: Settings = Depends(get_settings)):
    """获取前端需要的、公开的后端配置信息。"""
    return PublicConfig(
        enable_registration=settings.ENABLE_REGISTRATION,
        project_name=settings.MAIL_FROM_NAME
    )


# --- 新增：Minecraft 头像代理接口 ---
@app.get("/avatars/mc/{username}", tags=["Public"])
async def get_mc_avatar(username: str, settings: Settings = Depends(get_settings)):
    """
    一个代理接口，用于从 cravatar.eu 获取 Minecraft 头像，以避免客户端跨域或网络问题。
    """
    avatar_url = settings.MC_AVATAR_URL_TEMPLATE.format(username=username)

    async with httpx.AsyncClient() as client:
        try:
            req = client.build_request("GET", avatar_url, timeout=10.0)
            r = await client.send(req, stream=True)
            r.raise_for_status()

            return StreamingResponse(r.aiter_bytes(), headers=r.headers)

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Avatar not found.")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Could not fetch avatar from upstream server: {e}")


# --- 认证相关端点 ---
AUTH_TAGS = ["Authentication"]


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=AUTH_TAGS)
async def register_user(
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
        settings: Settings = Depends(get_settings)
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

    # crud.create_user 内部将处理 created_at 和 updated_at 为 offset-naive
    db_user = await crud.create_user(db=session, user_create=user_create)

    raw_token = generate_email_verification_token(db_user.email)

    # 获取当前 UTC 时间，并去除时区信息，用于 expires_at 字段
    expires_at_naive = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=settings.EMAIL_TOKEN_MAX_AGE_SECONDS)).replace(tzinfo=None)

    await crud.create_verification_token(
        db=session,
        user_id=db_user.id,
        token_hash=get_password_hash(raw_token),
        expires_at=expires_at_naive  # 修改为去除时区信息的 datetime
    )
    background_tasks.add_task(send_verification_email, email_to=db_user.email, username=db_user.username,
                              token=raw_token)
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
    user.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)  # 修改这里
    await session.commit()
    await session.refresh(user)

    db_token = await crud.get_verification_token_by_hash(db=session, token_hash=get_password_hash(token))
    if db_token:
        await crud.delete_db_token(db=session, token=db_token)

    return {"message": "邮箱验证成功！您现在可以登录了。"}


@app.post("/auth/token", response_model=Token, tags=AUTH_TAGS)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_async_session)):
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
                                 session: AsyncSession = Depends(get_async_session),
                                 settings: Settings = Depends(get_settings)):
    user = await crud.get_user_by_email(db=session, email=reset_request.email)
    if user:
        try:
            raw_token = generate_password_reset_token(user.email)
            # 获取当前 UTC 时间，并去除时区信息，用于 expires_at 字段
            expires_at_naive = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                seconds=settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS)).replace(tzinfo=None)
            await crud.create_password_reset_token(
                db=session,
                user_id=user.id,
                token_hash=get_password_hash(raw_token),
                expires_at=expires_at_naive  # 修改为去除时区信息的 datetime
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
async def update_user_me(user_update: UserUpdate, session: AsyncSession = Depends(get_async_session),
                         current_user: User = Depends(get_current_active_user)):
    if not user_update.model_dump(exclude_unset=True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有提供需要更新的数据")
    if user_update.mc_name and user_update.mc_name != current_user.mc_name:
        existing_user = await crud.get_user_by_mc_name(db=session, mc_name=user_update.mc_name)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该 Minecraft 用户名已被其他用户关联")

    return await crud.update_user(db=session, user=current_user, user_update=user_update)


@app.post("/users/me/change-password", status_code=status.HTTP_200_OK, tags=USERS_TAGS)
async def change_current_user_password(password_update: UserPasswordUpdate,
                                       session: AsyncSession = Depends(get_async_session),
                                       current_user: User = Depends(get_current_active_user)):
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")
    await crud.update_user_password(db=session, user=current_user, new_password=password_update.new_password)
    return {"message": "密码已成功更新"}


# --- 画廊功能端点 ---
GALLERY_TAGS = ["Gallery"]


def create_image_thumbnail(
        original_image_path: Path,
        thumbnail_save_path: Path,
        size: tuple[int, int] = (400, 400)
):
    """为图片文件创建缩略图"""
    try:
        with PILImage.open(original_image_path) as img:
            img.thumbnail(size, Resampling.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumbnail_save_path)
            logger.info(f"图片缩略图已保存到: {thumbnail_save_path}")
            return True
    except Exception as e:
        logger.error(f"创建图片缩略图失败: {e}")
        return False


def create_video_thumbnail(
        video_path: Path,
        thumbnail_save_path: Path,
        size: tuple[int, int] = (400, 400)
) -> bool:
    """为视频文件创建缩略图 (封面)"""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"无法打开视频文件: {video_path}")
            return False

        ret, frame = cap.read()
        if not ret:
            logger.error(f"无法从视频读取帧: {video_path}")
            cap.release()
            return False

        frame_pil = PILImage.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_pil.thumbnail(size, Resampling.LANCZOS)
        frame_pil.save(thumbnail_save_path)

        cap.release()
        logger.info(f"视频封面已保存到: {thumbnail_save_path}")
        return True
    except Exception as e:
        logger.error(f"创建视频封面失败: {e}")
        return False


@app.post("/gallery/upload", response_model=GalleryItemReadWithBuilder, status_code=status.HTTP_201_CREATED,
          tags=GALLERY_TAGS)
async def upload_gallery_item(
        background_tasks: BackgroundTasks,
        title: str = File(...),
        builder_name: str = File(...),
        description: Optional[str] = File(None),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_active_user),
        settings: Settings = Depends(get_settings)
):
    # 1. 文件类型和大小验证 (保持不变)
    if image.content_type not in settings.allowed_mime_types_list:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {image.content_type}.")
    max_file_size_bytes = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024
    if image.size > max_file_size_bytes:
        raise HTTPException(status_code=400, detail=f"文件过大，最大允许 {settings.UPLOAD_MAX_SIZE_MB}MB.")

    # 2. 确定文件类型和文件名
    item_type = ItemType.VIDEO if image.content_type.startswith("video/") else ItemType.IMAGE
    file_extension = Path(image.filename).suffix.lower() or ".dat"
    unique_filename_base = str(uuid.uuid4())
    original_filename = f"{unique_filename_base}{file_extension}"
    thumbnail_filename = f"{unique_filename_base}_thumb.jpg"  # 缩略图统一为 jpg
    original_file_location = UPLOAD_DIR / original_filename
    thumbnail_file_location = UPLOAD_DIR / thumbnail_filename

    # 3. 保存原始文件
    try:
        with open(original_file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise HTTPException(status_code=500, detail="上传文件时发生服务器内部错误。")
    finally:
        image.file.close()

    # 4. 准备画廊项目数据并存入数据库
    member = await crud.get_or_create_member(db=session, name=builder_name)
    image_url_to_store = f"/uploads/{original_filename}"
    thumbnail_url_to_store = f"/uploads/{thumbnail_filename}"  # 预设缩略图URL

    item_create_data = GalleryItemCreate(
        title=title,
        description=description,
        image_url=image_url_to_store,
        thumbnail_url=thumbnail_url_to_store,  # 先将URL存入数据库
        item_type=item_type
    )

    # 存入数据库并立即返回响应，不再等待缩略图生成
    db_gallery_item = await crud.create_gallery_item(
        db=session,
        item_create=item_create_data,
        user_id=current_user.id,
        member_id=member.id
    )

    # --- 5. 将耗时的缩略图生成任务添加到后台 ---
    background_tasks.add_task(
        process_thumbnail_in_background,
        original_file_location,
        thumbnail_file_location,
        item_type
    )

    await session.refresh(db_gallery_item, attribute_names=["builder"])

    # 立即返回响应给用户
    return db_gallery_item


class PaginatedGalleryItems(SQLModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GalleryItemReadWithBuilder]


@app.get("/gallery/items", response_model=PaginatedGalleryItems, tags=GALLERY_TAGS)
async def get_gallery_items(
        session: AsyncSession = Depends(get_async_session),
        settings: Settings = Depends(get_settings),
        page: int = Query(1, ge=1),
        page_size: int = Query(None, ge=1)
):
    effective_page_size = page_size if page_size is not None else settings.GALLERY_DEFAULT_PAGE_SIZE
    if effective_page_size > settings.GALLERY_MAX_PAGE_SIZE:
        effective_page_size = settings.GALLERY_MAX_PAGE_SIZE

    total_items, items = await crud.get_paginated_gallery_items(db=session, page=page, page_size=effective_page_size)
    total_pages = (total_items + effective_page_size - 1) // effective_page_size
    return PaginatedGalleryItems(total_items=total_items, total_pages=total_pages, page=page,
                                 page_size=effective_page_size, items=items)


# --- 新增：画廊项目管理端点 (更新和删除) ---
class GalleryItemUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None


@app.patch("/gallery/items/{item_id}", response_model=GalleryItemReadWithBuilder, tags=GALLERY_TAGS)
async def update_gallery_item(item_id: int, item_update: GalleryItemUpdate,
                              session: AsyncSession = Depends(get_async_session),
                              current_user: User = Depends(get_current_active_user)):
    db_item = await crud.get_gallery_item_by_id(db=session, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目未找到")
    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此项目")
    return await crud.update_gallery_item(db=session, item=db_item, item_update=item_update)


@app.delete("/gallery/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=GALLERY_TAGS)
async def delete_gallery_item(item_id: int, session: AsyncSession = Depends(get_async_session),
                              current_user: User = Depends(get_current_active_user)):
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
async def create_member(member_data: MemberCreate, session: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(get_current_active_user)):
    if await crud.get_member_by_name(db=session, name=member_data.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该名称的成员已存在")

    # 直接将 member_data 传递给 crud 函数，让 crud 函数处理创建逻辑
    db_member = await crud.create_member(db=session, member_data=member_data)
    return db_member


@app.get("/members", response_model=List[MemberRead], tags=MEMBERS_TAGS)
async def get_all_members(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_all_members(db=session)


@app.patch("/members/{member_id}", response_model=MemberRead, tags=MEMBERS_TAGS)
async def update_member(member_id: int, member_update: MemberUpdate, session: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(get_current_active_user)):
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


# --- 创建一个专门用于后台生成缩略图的函数 ---
def process_thumbnail_in_background(
    original_file_path: Path,
    thumbnail_save_path: Path,
    item_type: ItemType
):
    """
    根据项目类型，在后台生成图片或视频的缩略图。
    """
    logger.info(f"后台任务开始: 为 {original_file_path} 生成缩略图...")
    if item_type == ItemType.IMAGE:
        create_image_thumbnail(original_file_path, thumbnail_save_path)
    elif item_type == ItemType.VIDEO:
        create_video_thumbnail(original_file_path, thumbnail_save_path)
    logger.info(f"后台任务结束: 缩略图处理完成。")


# --- V2: 自定义管理面板 API ---

class AdminUserUpdate(SQLModel):
    """用于管理员更新用户信息的模型"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


@app.get("/api/admin/users", response_model=List[UserRead], tags=["Admin Panel"])
async def admin_get_users(
        skip: int = 0,
        limit: int = 100,
        session: AsyncSession = Depends(get_async_session),
        admin_user: User = Depends(get_current_admin_user),
):
    """(管理员) 获取用户列表"""
    users = await session.execute(select(User).offset(skip).limit(limit))
    return users.scalars().all()


@app.patch("/api/admin/users/{user_id}", response_model=UserRead, tags=["Admin Panel"])
async def admin_update_user(
        user_id: int,
        user_update: AdminUserUpdate,  # <--- This should now work correctly
        session: AsyncSession = Depends(get_async_session),
        admin_user: User = Depends(get_current_admin_user),
):
    """(管理员) 更新指定用户信息"""
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户未找到")

    # Use the specific CRUD function for admin updates
    # Note: We can reuse the `admin_update_user_details` from crud.py if you created it,
    # or just perform the logic here directly.
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.delete("/api/admin/users/{user_id}", status_code=status.HTTP_200_OK, tags=["Admin Panel"])
async def admin_delete_user(
        user_id: int,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
        admin_user: User = Depends(get_current_admin_user),
):
    """(管理员) 删除指定用户及其所有作品"""
    if admin_user.id == user_id:
        raise HTTPException(status_code=400, detail="管理员不能删除自己。")

    # 使用 CRUD 函数执行删除操作
    deleted_user = await crud.delete_user_by_id(db=session, user_id=user_id)

    if not deleted_user:
        raise HTTPException(status_code=404, detail="用户未找到")

    # 在后台发送邮件通知
    background_tasks.add_task(
        send_account_deletion_email,
        email_to=deleted_user.email,
        username=deleted_user.username
    )

    return {"message": f"用户 {deleted_user.username} 已被成功删除。"}


# --- 画廊管理 API ---

@app.get("/api/admin/gallery-items", response_model=List[GalleryItemReadWithBuilder], tags=["Admin Panel"])
async def admin_get_gallery_items(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(get_current_admin_user),
):
    """(管理员) 获取所有画廊作品的列表"""
    result = await session.execute(
        select(models.GalleryItem)
        .options(
            selectinload(models.GalleryItem.builder),
            selectinload(models.GalleryItem.uploader)
        )
        .order_by(desc(models.GalleryItem.uploaded_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@app.delete("/api/admin/gallery-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin Panel"])
async def admin_delete_gallery_item(
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(get_current_admin_user),
):
    """(管理员) 删除指定的画廊作品"""
    db_item = await session.get(models.GalleryItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="画廊作品未找到")

    # 在删除数据库记录前，先删除关联的物理文件
    try:
        # UPLOAD_DIR 已在文件顶部定义
        if db_item.image_url:
            image_path = UPLOAD_DIR / Path(db_item.image_url).name
            if image_path.is_file():
                image_path.unlink()
        if db_item.thumbnail_url:
            thumb_path = UPLOAD_DIR / Path(db_item.thumbnail_url).name
            if thumb_path.is_file():
                thumb_path.unlink()
    except Exception as e:
        # 即使文件删除失败，也应继续删除数据库记录，但要记录错误
        logger.error(f"删除作品 {item_id} 的文件时出错: {e}")

    await session.delete(db_item)
    await session.commit()
    return


# --- 站点配置管理 API ---

@app.get("/api/admin/site-config", response_model=dict, tags=["Admin Panel"])
async def admin_get_site_config(admin_user: User = Depends(get_current_admin_user)):
    if not SITE_CONFIG_PATH.exists():
        raise HTTPException(status_code=404, detail="site-config.json not found")
    try:
        with open(SITE_CONFIG_PATH, "r", encoding="utf-8-sig") as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except Exception as e:
        logger.error(f"读取或解析 site-config.json 时发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"读取配置文件时发生未知服务器错误。")


@app.post("/api/admin/site-config", status_code=status.HTTP_200_OK, tags=["Admin Panel"])
async def admin_update_site_config(
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
):
    try:
        new_config = await request.json()
        with open(SITE_CONFIG_PATH, "w", encoding="utf-8") as f: # 写入时用 utf-8 即可，它不会主动加BOM
            json.dump(new_config, f, ensure_ascii=False, indent=2)
        return {"message": "站点配置已成功更新！"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="提供的内容不是有效的JSON格式。")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件时发生错误: {e}")



# --- 用于直接运行 Uvicorn (主要用于开发) ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )