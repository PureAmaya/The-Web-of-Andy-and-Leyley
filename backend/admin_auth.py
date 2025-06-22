# backend/admin_auth.py
from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from backend.auth_utils import  verify_password, create_access_token
from backend.core.config import get_settings
from backend.crud import get_user_by_username
from backend.database import get_async_session
from backend.models import UserRole

settings = get_settings()

# 这是 SQLAdmin 用来存储会话令牌的密钥，应该是保密的
SECRET_KEY = settings.JWT_SECRET_KEY



class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        async for session in get_async_session():  # 获取异步会话
            user = await get_user_by_username(db=session, username=username)

        if not user:
            return False

        # 验证密码和角色
        if not verify_password(password, user.hashed_password):
            return False
        if user.role != UserRole.ADMIN:
            return False

        # 创建并存储令牌
        access_token = create_access_token({"sub_id": user.id, "is_admin": True})
        request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # 这里您可以添加更复杂的令牌验证逻辑，
        # 例如，解码令牌并再次检查用户的管理员状态。
        # 为简化起见，我们信任会话中的令牌。

        return None


authentication_backend = AdminAuth(secret_key=SECRET_KEY)