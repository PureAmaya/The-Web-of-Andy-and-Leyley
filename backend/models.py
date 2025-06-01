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
    username: str = Field(description="用户名")  # 移除 unique=True, 在 User 模型中通过 __table_args__ 定义
    email: str = Field(description="邮箱")  # 移除 unique=True, 在 User 模型中通过 __table_args__ 定义
    full_name: Optional[str] = Field(default=None, description="全名")
    bio: Optional[str] = Field(default=None, description="个人简介")
    avatar_url: Optional[str] = Field(default=None, description="头像图片链接 (必须是有效的URL或None)")
    is_active: bool = Field(default=True, description="账户是否激活")
    is_verified: bool = Field(default=False, description="邮箱是否已验证")


class User(UserBase, table=True):
    """
    数据库中的 User 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID，主键")  # primary_key=True 会隐式创建索引
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


    # 新增：与 GalleryItem 的反向关系
    # 这允许我们通过 user.gallery_items 访问该用户上传的所有画廊作品
    gallery_items: List["GalleryItem"] = Relationship(back_populates="uploader")  # <--- 4. 添加反向关系

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
        if hasattr(data, 'new_password') and hasattr(data, 'new_password_confirm'):  # 确保字段存在
            if data.new_password != data.new_password_confirm:
                raise ValueError('新密码和确认密码不匹配')
        return data


# --- 邮件验证令牌模型 ---

class VerificationTokenBase(SQLModel):
    """
    邮件验证令牌的基础字段。
    """
    token_hash: str = Field(description="验证令牌的哈希值")  # 移除 unique=True
    expires_at: datetime.datetime = Field(description="令牌过期时间 (UTC)")


class VerificationToken(VerificationTokenBase, table=True):
    """
    数据库中的 VerificationToken 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="令牌记录ID，主键")
    user_id: int = Field(foreign_key="user.id", index=True, description="关联的用户ID")  # 普通索引用于加速外键查询

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
    token_hash: str = Field(description="密码重置令牌的哈希值")  # 移除 unique=True
    expires_at: datetime.datetime = Field(description="令牌过期时间 (UTC)")


class PasswordResetToken(PasswordResetTokenBase, table=True):
    """
    数据库中的 PasswordResetToken 表模型。
    """
    id: Optional[int] = Field(default=None, primary_key=True, description="令牌记录ID，主键")
    user_id: int = Field(foreign_key="user.id", index=True, description="关联的用户ID")  # 普通索引用于加速外键查询

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
        if hasattr(data, 'new_password') and hasattr(data, 'new_password_confirm'):  # 确保字段存在
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


# --- 新增：画廊项目模型 ---

class GalleryItemBase(SQLModel):
    title: str = Field(index=True, description="作品标题")
    description: Optional[str] = Field(default=None, description="作品描述")
    # file_path: str # 指向原始文件的路径，具体存储策略后续确定
    # thumbnail_path: str # 指向缩略图的路径
    # mime_type: str # 例如 image/jpeg, image/png
    # file_size: int # 单位字节

    # 根据技术设计报告 III.A，先定义核心元数据
    # file_path, thumbnail_path, mime_type, file_size 字段的精确定义
    # 会依赖于我们后续确定的文件存储和处理策略。
    # 为简单起见，我们暂时用占位符或更通用的字段，稍后细化。

    # 替代方案：先定义一些基本的可展示信息
    image_url: str = Field(description="图片展示URL (可能是原始文件或优化后的版本)")  #
    thumbnail_url: Optional[str] = Field(default=None, description="缩略图URL")  #


class GalleryItem(GalleryItemBase, table=True):
    """
    数据库中的 GalleryItem 表模型。
    """
    # 表名将是 'galleryitem'
    id: Optional[int] = Field(default=None, primary_key=True, description="画廊项目ID，主键")

    user_id: int = Field(foreign_key="user.id", index=True, description="上传用户的ID")  #

    # 建立与 User 模型的关系
    # 这允许我们通过 gallery_item.user 来访问上传该作品的用户对象
    # 并且在 User 模型中可以通过 user.gallery_items (如果定义了反向关系) 访问用户的所有作品
    uploader: Optional["User"] = Relationship(back_populates="gallery_items")  # <--- 3. 定义关系

    uploaded_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="上传时间 (UTC)"
    )  #
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(timezone.utc),
        nullable=False,
        description="最后更新时间 (UTC)"
    )  #

    # 根据技术设计报告 III.A，其他建议字段（我们后续可以逐步添加和细化）:
    # file_path: str # 存储中原始上传文件的路径
    # thumbnail_path: str # 生成的缩略图的路径
    # mime_type: str # 例如 image/jpeg, image/png
    # file_size: int # 单位字节

    __table_args__ = ({'extend_existing': True},)  # 保持与其他表模型一致




# --- 用于API交互的 GalleryItem 模型 ---

class GalleryItemCreate(GalleryItemBase):
    """
    用于创建新的画廊项目时接收的请求体模型。
    user_id 将从当前登录用户获取，不需要客户端提供。
    """
    pass  # 字段已在 GalleryItemBase 中定义，如果需要额外字段可以在这里添加


class GalleryItemRead(GalleryItemBase):
    """
    用于从 API 读取/返回画廊项目数据时的响应体模型。
    """
    id: int
    user_id: int
    uploaded_at: datetime.datetime
    updated_at: datetime.datetime
    # 可以考虑在这里也返回上传者的一些基本信息 (例如，通过嵌套的 UserRead 模型)
    # uploader: Optional[UserRead] = None # 如果希望在读取画廊项目时直接嵌入用户信息


class GalleryItemReadWithUploader(GalleryItemRead):  # 一个更具体的读取模型，包含上传者信息
    """
    读取画廊项目时，同时返回上传者的公开信息。
    """
    uploader: Optional[UserRead] = None  # 使用 UserRead 来避免返回哈希密码等敏感信息
