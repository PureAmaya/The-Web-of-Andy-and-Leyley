# backend/crud.py

import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend import models
from backend.auth_utils import get_password_hash


# --- User CRUD ---

async def get_user_by_mc_name(db: AsyncSession, mc_name: str) -> Optional[models.User]:
    """通过 Minecraft 用户名获取用户"""
    result = await db.exec(select(models.User).where(models.User.mc_name == mc_name))
    return result.first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """通过 ID 获取用户"""
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """通过邮箱获取用户"""
    result = await db.exec(select(models.User).where(models.User.email == email))
    return result.first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    """通过用户名获取用户"""
    result = await db.exec(select(models.User).where(models.User.username == username))
    return result.first()


async def create_user(db: AsyncSession, user_create: models.UserCreate) -> models.User:
    """创建一个新用户"""
    hashed_password = get_password_hash(user_create.password)

    # model_validate 时，强制覆盖角色为 'user'
    db_user = models.User.model_validate(
        user_create,
        update={
            "hashed_password": hashed_password,
            "is_verified": False,
            "is_active": True,
            "role": models.UserRole.USER  # <--- 强制设置为普通用户
        }
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def update_user(db: AsyncSession, user: models.User, user_update: models.UserUpdate) -> models.User:
    """更新用户信息"""
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: models.User, new_password: str) -> models.User:
    """更新用户密码"""
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(user)
    await db.commit()
    return user


# --- Token CRUD ---

async def create_verification_token(db: AsyncSession, user_id: int, token_hash: str,
                                    expires_at: datetime.datetime) -> models.VerificationToken:
    """创建邮件验证令牌"""
    token = models.VerificationToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    await db.commit()
    return token


async def get_verification_token_by_hash(db: AsyncSession, token_hash: str) -> Optional[models.VerificationToken]:
    """通过哈希值获取邮件验证令牌"""
    result = await db.exec(select(models.VerificationToken).where(models.VerificationToken.token_hash == token_hash))
    return result.first()


async def create_password_reset_token(db: AsyncSession, user_id: int, token_hash: str,
                                      expires_at: datetime.datetime) -> models.PasswordResetToken:
    """创建密码重置令牌"""
    # 先删除该用户已有的令牌
    existing_tokens_result = await db.exec(
        select(models.PasswordResetToken).where(models.PasswordResetToken.user_id == user_id))
    for t in existing_tokens_result.all():
        await db.delete(t)

    # 创建新令牌
    token = models.PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    await db.commit()
    return token


async def get_password_reset_token_by_hash(db: AsyncSession, token_hash: str) -> Optional[models.PasswordResetToken]:
    """通过哈希值获取密码重置令牌"""
    result = await db.exec(select(models.PasswordResetToken).where(models.PasswordResetToken.token_hash == token_hash))
    return result.first()


async def delete_db_token(db: AsyncSession, token: models.VerificationToken | models.PasswordResetToken):
    """从数据库中删除一个令牌"""
    await db.delete(token)
    await db.commit()


# --- Member CRUD ---

async def get_member_by_id(db: AsyncSession, member_id: int) -> Optional[models.Member]:
    """通过 ID 获取成员"""
    return await db.get(models.Member, member_id)


async def get_member_by_name(db: AsyncSession, name: str) -> Optional[models.Member]:
    """通过名称获取成员"""
    result = await db.exec(select(models.Member).where(func.lower(models.Member.name) == func.lower(name)))
    return result.first()


async def get_or_create_member(db: AsyncSession, name: str) -> models.Member:
    """获取或创建成员"""
    member = await get_member_by_name(db, name)
    if not member:
        member = models.Member(name=name)
        db.add(member)
        await db.commit()
        await db.refresh(member)
    return member


async def get_all_members(db: AsyncSession) -> List[models.Member]:
    """获取所有成员"""
    result = await db.exec(select(models.Member))
    return result.all()


async def update_member(db: AsyncSession, member: models.Member, member_update: models.MemberUpdate) -> models.Member:
    """更新成员信息"""
    update_data = member_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def delete_member(db: AsyncSession, member: models.Member):
    """删除成员"""
    await db.delete(member)
    await db.commit()


# --- GalleryItem CRUD ---

async def get_gallery_item_by_id(db: AsyncSession, item_id: int) -> Optional[models.GalleryItem]:
    """通过 ID 获取画廊作品"""
    return await db.get(models.GalleryItem, item_id)


async def get_paginated_gallery_items(db: AsyncSession, page: int, page_size: int) -> (int, List[models.GalleryItem]):
    """分页获取画廊作品"""
    offset = (page - 1) * page_size

    # 获取总数
    total_items_statement = select(func.count(models.GalleryItem.id))
    total_items_result = await db.exec(total_items_statement)
    total_items = total_items_result.one_or_none() or 0

    if total_items == 0:
        return 0, []

    # 获取分页数据
    items_statement = (
        select(models.GalleryItem)
        .options(
            selectinload(models.GalleryItem.builder),  # 预先加载 builder
            selectinload(models.GalleryItem.uploader)  # 预先加载 uploader
        )
        .order_by(models.GalleryItem.uploaded_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items_result = await db.exec(items_statement)
    gallery_items_db = items_result.all()

    return total_items, gallery_items_db


async def create_gallery_item(db: AsyncSession, item_create: models.GalleryItemCreate, user_id: int,
                              member_id: int) -> models.GalleryItem:
    """创建画廊作品"""
    db_item = models.GalleryItem.model_validate(
        item_create,
        update={"user_id": user_id, "member_id": member_id}
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def update_gallery_item(db: AsyncSession, item: models.GalleryItem,
                              item_update: models.GalleryItemUpdate) -> models.GalleryItem:
    """更新画廊作品"""
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    item.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_gallery_item(db: AsyncSession, item: models.GalleryItem):
    """删除画廊作品"""
    await db.delete(item)
    await db.commit()


async def get_friend_links(db: AsyncSession) -> list[models.FriendLink]:
    """获取所有友情链接，按显示顺序排序"""
    result = await db.execute(select(models.FriendLink).order_by(models.FriendLink.display_order))
    return result.scalars().all()