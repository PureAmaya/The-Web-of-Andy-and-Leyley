# backend/models.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, Any, List
import datetime
from datetime import timezone  # 用于 timezone-aware datetime 对象
from pydantic import model_validator
from sqlalchemy import UniqueConstraint  # 导入 UniqueConstraint


# --- 用户模型 ---

class UserBase(SQLModel):
    """
    用户模型的基础字段，用于数据校验和共享。
    """
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱")
    full_name: Optional[str] = Field(default=None, description="全名")
    bio: Optional[str] = Field(default=None, description="个人简介")
    avatar_url: Optional[str] = Field(default=None, description="头像图片链接 (必须是有效的URL或None)")
    is_active: bool = Field(default=True, description="账户是否激活")
    is_verified: bool = Field(default=False, description="邮箱是否已验证")


class User(UserBase, table=True):
    """
    数据库中的 User 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID，主键")
    hashed_password: str = Field(description="哈希后的密码")

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="创建时间 (UTC)"
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="最后更新时间 (UTC)"
    )

    gallery_items: List["GalleryItem"] = Relationship(back_populates="uploader")

    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
        {'extend_existing': True}
    )


class UserCreate(UserBase):
    """
    用于创建用户时接收的请求体模型。
    """
    password: str = Field(min_length=8, description="用户密码，至少8位")


class UserRead(UserBase):
    """
    用于从 API 读取/返回用户数据时的响应体模型。
    """
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool # 确保 UserRead 也包含这些从 UserBase 继承的字段
    is_verified: bool


class UserUpdate(SQLModel):
    """
    用于更新用户个人资料时接收的请求体模型。
    所有字段都是可选的。
    """
    full_name: Optional[str] = Field(default=None, description="新的全名")
    bio: Optional[str] = Field(default=None, description="新的个人简介")
    avatar_url: Optional[str] = Field(default=None, description="新的头像图片链接 (必须是有效的URL或None)")


class UserPasswordUpdate(SQLModel):
    """
    用于用户更新自己密码时接收的请求体模型。
    """
    current_password: str = Field(description="用户当前密码")
    new_password: str = Field(min_length=8, description="新密码，至少8位")
    new_password_confirm: str = Field(description="确认新密码")

    @model_validator(mode='after')
    def check_passwords_match(cls, data: Any) -> Any:
        if hasattr(data, 'new_password') and hasattr(data, 'new_password_confirm'):
            if data.new_password != data.new_password_confirm:
                raise ValueError('新密码和确认密码不匹配')
        return data


# --- 邮件验证令牌模型 ---

class VerificationTokenBase(SQLModel):
    """
    邮件验证令牌的基础字段。
    """
    token_hash: str = Field(description="验证令牌的哈希值")
    expires_at: datetime.datetime = Field(description="令牌过期时间 (UTC)")


class VerificationToken(VerificationTokenBase, table=True):
    """
    数据库中的 VerificationToken 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="令牌记录ID，主键")
    user_id: int = Field(foreign_key="user.id", index=True, description="关联的用户ID")

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="令牌创建时间 (UTC)"
    )
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_verificationtoken_token_hash"),
        {'extend_existing': True}
    )


class VerificationTokenCreate(VerificationTokenBase):
    """
    用于创建验证令牌记录时的数据模型。
    """
    user_id: int


class VerificationTokenRead(VerificationTokenBase):
    """
    用于从API读取/返回验证令牌信息时的模型。
    """
    id: int
    user_id: int
    created_at: datetime.datetime


# --- 密码重置令牌模型 ---

class PasswordResetTokenBase(SQLModel):
    """
    密码重置令牌的基础字段。
    """
    token_hash: str = Field(description="密码重置令牌的哈希值")
    expires_at: datetime.datetime = Field(description="令牌过期时间 (UTC)")


class PasswordResetToken(PasswordResetTokenBase, table=True):
    """
    数据库中的 PasswordResetToken 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="令牌记录ID，主键")
    user_id: int = Field(foreign_key="user.id", index=True, description="关联的用户ID")

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="令牌创建时间 (UTC)"
    )
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_passwordresettoken_token_hash"),
        {'extend_existing': True}
    )


class PasswordResetTokenCreate(PasswordResetTokenBase):
    """
    用于创建密码重置令牌记录时的数据模型。
    """
    user_id: int


class PasswordResetTokenRead(PasswordResetTokenBase):
    id: int
    user_id: int
    created_at: datetime.datetime


class PasswordResetRequest(SQLModel):
    """
    请求密码重置时接收用户邮箱的模型。
    """
    email: str


class PasswordResetForm(SQLModel):
    """
    用户提交新密码和密码重置令牌时使用的模型。
    """
    token: str = Field(description="从邮件中获取的密码重置令牌")
    new_password: str = Field(min_length=8, description="新密码，至少8位")
    new_password_confirm: str = Field(description="确认新密码")

    @model_validator(mode='after')
    def check_passwords_match(cls, data: Any) -> Any:
        if hasattr(data, 'new_password') and hasattr(data, 'new_password_confirm'):
            if data.new_password != data.new_password_confirm:
                raise ValueError('新密码和确认密码不匹配')
        return data


# --- JWT Token 相关模型 ---

class Token(SQLModel):
    """
    用于 API 响应中返回 JWT 令牌的数据模型。
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """
    解码 JWT 访问令牌或刷新令牌后得到的数据模型。
    """
    user_id: Optional[int] = None


class RefreshTokenRequest(SQLModel):
    """
    用于接收刷新令牌请求的请求体模型。
    """
    refresh_token: str = Field(description="用户持有的刷新令牌")


# --- 画廊项目模型 ---

class GalleryItemBase(SQLModel):
    title: str = Field(index=True, description="作品标题") # 普通索引用于查询标题
    description: Optional[str] = Field(default=None, description="作品描述")
    image_url: str = Field(description="图片展示URL")
    thumbnail_url: Optional[str] = Field(default=None, description="缩略图URL")


class GalleryItem(GalleryItemBase, table=True):
    """
    数据库中的 GalleryItem 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="画廊项目ID，主键")
    user_id: int = Field(foreign_key="user.id", index=True, description="上传用户的ID")

    uploader: Optional["User"] = Relationship(back_populates="gallery_items") # 使用简单字符串引用

    uploaded_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="上传时间 (UTC)"
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="最后更新时间 (UTC)"
    )

    # 如果 GalleryItem 表没有自己的 UniqueConstraint，可以直接使用字典
    __table_args__ = {'extend_existing': True}


class GalleryItemCreate(GalleryItemBase):
    """
    用于创建新的画廊项目时接收的请求体模型。
    """
    pass


class GalleryItemRead(GalleryItemBase):
    """
    用于从 API 读取/返回画廊项目数据时的响应体模型。
    """
    id: int
    user_id: int
    uploaded_at: datetime.datetime
    updated_at: datetime.datetime
    # 确保 UserRead 中定义了 is_active 和 is_verified 以便正确序列化
    # 或者在这里定义一个更精简的嵌套 uploader 模型


class GalleryItemReadWithUploader(GalleryItemRead):
    """
    读取画廊项目时，同时返回上传者的公开信息。
    """
    uploader: Optional[UserRead] = None