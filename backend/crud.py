# backend/crud.py
import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import func, desc, update
from sqlalchemy.orm import selectinload
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from backend import models
from backend.auth_utils import get_password_hash


# --- User CRUD ---

async def get_user_by_mc_name(db: AsyncSession, mc_name: str) -> Optional[models.User]:
    """通过 Minecraft 用户名获取用户"""
    result = await db.execute(select(models.User).where(models.User.mc_name == mc_name))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """通过 ID 获取用户"""
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """通过邮箱获取用户"""
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    """通过用户名获取用户"""
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_create: models.UserCreate) -> models.User:
    """创建一个新用户"""
    hashed_password = get_password_hash(user_create.password)
    current_utc_naive = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    existing_users_count_result = await db.execute(select(func.count(models.User.id)))
    existing_users_count = existing_users_count_result.scalar_one_or_none() or 0

    user_role = models.UserRole.ADMIN if existing_users_count == 0 else models.UserRole.USER

    db_user = models.User.model_validate(
        user_create,
        update={
            "hashed_password": hashed_password, "is_verified": False, "is_active": True,
            "role": user_role, "created_at": current_utc_naive, "updated_at": current_utc_naive
        }
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user: models.User, user_update: models.UserUpdate) -> models.User:
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: models.User, new_password: str) -> models.User:
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --- Token CRUD ---

async def create_verification_token(db: AsyncSession, user_id: int, token_hash: str,
                                    expires_at: datetime.datetime) -> models.VerificationToken:
    if expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=None)
    token = models.VerificationToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def get_verification_token_by_hash(db: AsyncSession, token_hash: str) -> Optional[models.VerificationToken]:
    """通过哈希值获取邮件验证令牌"""
    result = await db.execute(select(models.VerificationToken).where(models.VerificationToken.token_hash == token_hash))
    return result.scalars().first()


async def create_password_reset_token(db: AsyncSession, user_id: int, token_hash: str,
                                      expires_at: datetime.datetime) -> models.PasswordResetToken:
    """创建密码重置令牌"""
    existing_tokens_result = await db.execute(
        select(models.PasswordResetToken).where(models.PasswordResetToken.user_id == user_id))
    for t in existing_tokens_result.scalars().all():
        await db.delete(t)
    if expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=None)
    token = models.PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def get_password_reset_token_by_hash(db: AsyncSession, token_hash: str) -> Optional[models.PasswordResetToken]:
    """通过哈希值获取密码重置令牌"""
    result = await db.execute(
        select(models.PasswordResetToken).where(models.PasswordResetToken.token_hash == token_hash))
    return result.scalars().first()


async def delete_db_token(db: AsyncSession, token: Union[models.VerificationToken, models.PasswordResetToken]):
    await db.delete(token)
    await db.commit()


# --- Member CRUD ---

async def get_member_by_id(db: AsyncSession, member_id: int) -> Optional[models.Member]:
    """通过 ID 获取成员"""
    return await db.get(models.Member, member_id)


async def get_member_by_name(db: AsyncSession, name: str) -> Optional[models.Member]:
    """通过名称获取成员"""
    result = await db.execute(select(models.Member).where(func.lower(models.Member.name) == func.lower(name)))
    return result.scalars().first()


async def get_or_create_member(db: AsyncSession, name: str) -> models.Member:
    member = await get_member_by_name(db, name)
    if not member:
        current_utc_naive = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        member = models.Member(name=name, created_at=current_utc_naive, updated_at=current_utc_naive)
        db.add(member)
        await db.commit()
        await db.refresh(member)
    return member


async def get_all_members(db: AsyncSession) -> List[models.Member]:
    """获取所有成员"""
    result = await db.execute(select(models.Member))
    return result.scalars().all()


async def update_member(db: AsyncSession, member: models.Member, member_update: models.MemberUpdate) -> models.Member:
    update_data = member_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    member.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def delete_member(db: AsyncSession, member: models.Member):
    """
    删除一个成员，并将其所有关联的画廊作品的 member_id 设置为 NULL。
    """
    # 1. 解除所有关联作品的作者外键
    await db.execute(
        update(models.GalleryItem)
        .where(models.GalleryItem.member_id == member.id)
        .values(member_id=None)
    )

    # 2. 现在可以安全地删除该成员了
    await db.delete(member)
    await db.commit()

# --- GalleryItem CRUD ---

async def get_gallery_item_by_id(db: AsyncSession, item_id: int) -> Optional[models.GalleryItem]:
    """通过 ID 获取画廊作品"""
    result = await db.execute(
        select(models.GalleryItem)
        .where(models.GalleryItem.id == item_id)
        .options(selectinload(models.GalleryItem.builder), selectinload(models.GalleryItem.uploader))
    )
    return result.scalars().first()


async def get_paginated_gallery_items(db: AsyncSession, page: int, page_size: int) -> Tuple[
    int, List[models.GalleryItem]]:
    """分页获取画廊作品"""
    offset = (page - 1) * page_size

    total_items_statement = select(func.count(models.GalleryItem.id))
    total_items_result = await db.execute(total_items_statement)
    total_items = total_items_result.scalar_one_or_none() or 0

    if total_items == 0:
        return 0, []

    items_statement = (
        select(models.GalleryItem)
        .options(
            selectinload(models.GalleryItem.builder),
            selectinload(models.GalleryItem.uploader)
        )
        .order_by(desc(models.GalleryItem.uploaded_at))
        .offset(offset)
        .limit(page_size)
    )
    items_result = await db.execute(items_statement)
    gallery_items_db = items_result.scalars().all()

    return total_items, gallery_items_db


async def create_gallery_item(db: AsyncSession, item_create: models.GalleryItemCreate, user_id: int,
                              member_id: int) -> models.GalleryItem:
    current_utc_naive = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db_item = models.GalleryItem.model_validate(
        item_create,
        update={
            "user_id": user_id, "member_id": member_id,
            "uploaded_at": current_utc_naive, "updated_at": current_utc_naive
        }
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def update_gallery_item(db: AsyncSession, item: models.GalleryItem,
                              item_update: models.GalleryItemUpdate) -> models.GalleryItem:
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    item.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_gallery_item(db: AsyncSession, item: models.GalleryItem):
    await db.delete(item)
    await db.commit()


# --- FriendLink CRUD ---

async def get_friend_links(db: AsyncSession) -> list[models.FriendLink]:
    """获取所有友情链接，按显示顺序排序"""
    result = await db.execute(select(models.FriendLink).order_by(models.FriendLink.display_order))
    return result.scalars().all()

# --- 新增的自定义管理面板 CRUD ---

async def admin_get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """获取所有用户的列表"""
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def admin_update_user_details(db: AsyncSession, user: models.User, update_data: models.AdminUserUpdate) -> models.User:
    """管理员更新用户信息"""
    patch_data = update_data.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(user, key, value)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """
    通过ID删除用户，并级联删除其所有关联记录（作品、令牌等）。
    返回被删除的用户对象，如果未找到则返回 None。
    """
    # 首先获取用户对象，以便后续返回其信息用于发送邮件
    user_to_delete = await db.get(models.User, user_id)
    if not user_to_delete:
        return None

    # 1. 删除关联的画廊作品
    gallery_items_stmt = select(models.GalleryItem).where(models.GalleryItem.user_id == user_id)
    for item in (await db.execute(gallery_items_stmt)).scalars().all():
        # 如果有物理文件，也应该在这里加入删除逻辑
        await db.delete(item)

    # 2. 删除关联的邮件验证令牌 (修复本次报错的关键)
    verification_tokens_stmt = select(models.VerificationToken).where(models.VerificationToken.user_id == user_id)
    for token in (await db.execute(verification_tokens_stmt)).scalars().all():
        await db.delete(token)

    # 3. 删除关联的密码重置令牌
    password_reset_tokens_stmt = select(models.PasswordResetToken).where(models.PasswordResetToken.user_id == user_id)
    for token in (await db.execute(password_reset_tokens_stmt)).scalars().all():
        await db.delete(token)

    # 4. 现在可以安全地删除用户了
    await db.delete(user_to_delete)
    await db.commit()

    return user_to_delete


