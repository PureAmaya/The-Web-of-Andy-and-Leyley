# backend/admin.py
from sqladmin import ModelView
from backend import models

class UserAdmin(ModelView, model=models.User):
    # 显示在列表页的列
    column_list = [
        models.User.id,
        models.User.username,
        models.User.email,
        models.User.mc_name,
        models.User.role,
        models.User.is_active,
        models.User.is_verified
    ]
    # 允许的搜索字段
    column_searchable_list = [models.User.username, models.User.email, models.User.mc_name]
    # 表单中排除的字段
    form_excluded_columns = [
        models.User.hashed_password,
        models.User.gallery_items,
        models.User.created_at,
        models.User.updated_at
    ]
    name = "用户"
    name_plural = "用户管理"
    icon = "fa-solid fa-user"

class MemberAdmin(ModelView, model=models.Member):
    column_list = [models.Member.id, models.Member.name, models.Member.role]
    column_searchable_list = [models.Member.name]
    name = "成员"
    name_plural = "成员管理"
    icon = "fa-solid fa-users"

class GalleryItemAdmin(ModelView, model=models.GalleryItem):
    column_list = [
        models.GalleryItem.id,
        models.GalleryItem.title,
        models.GalleryItem.uploader,
        models.GalleryItem.builder
    ]
    column_searchable_list = [models.GalleryItem.title]
    # 在表单中允许通过下拉框选择 uploader 和 builder
    form_columns = [
        models.GalleryItem.title,
        models.GalleryItem.description,
        models.GalleryItem.image_url,
        models.GalleryItem.thumbnail_url,
        models.GalleryItem.uploader, # 这会变成一个用户选择器
        models.GalleryItem.builder,   # 这会变成一个成员选择器
    ]
    name = "画廊作品"
    name_plural = "画廊管理"
    icon = "fa-solid fa-image"

# 新增 FriendLink 的管理视图
class FriendLinkAdmin(ModelView, model=models.FriendLink):
    column_list = [
        models.FriendLink.id,
        models.FriendLink.name,
        models.FriendLink.url,
        models.FriendLink.logo_url,
        models.FriendLink.display_order
    ]
    column_searchable_list = [models.FriendLink.name, models.FriendLink.url]
    form_columns = [
        models.FriendLink.name,
        models.FriendLink.url,
        models.FriendLink.logo_url,
        models.FriendLink.display_order
    ]
    name = "友情链接"
    name_plural = "友情链接管理"
    icon = "fa-solid fa-link"


admin_views = [UserAdmin, MemberAdmin, GalleryItemAdmin, FriendLinkAdmin]