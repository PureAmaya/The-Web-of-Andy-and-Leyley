# email_utils.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import logging

from core.config import settings  # 导入配置

# 1. 创建邮件连接配置
mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,  # 在生产环境中应为 True，确保与邮件服务器的连接安全
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME
)


async def send_email(subject: str, recipients: list[EmailStr], html_body: str):
    """
    通用的邮件发送函数。
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html_body,
        subtype=MessageType.html
    )

    fm = FastMail(mail_conf)
    try:
        await fm.send_message(message)
        logging.info(f"邮件已发送至: {', '.join(recipients)}, 主题: {subject}")
    except Exception as e:
        logging.error(f"邮件发送失败至: {', '.join(recipients)}, 主题: {subject}, 错误: {e}")
        # 在实际应用中，这里可能需要更健壮的错误处理，例如将失败的邮件放入重试队列


async def send_verification_email(email_to: EmailStr, username: str, token: str):
    """
    发送包含验证链接的邮件给新注册用户。
    """
    subject = f"{settings.MAIL_FROM_NAME} - 邮箱验证"
    # 构建验证链接，指向前端的验证页面
    verification_url = f"{settings.PORTAL_FRONTEND_BASE_URL}/verify-email?token={token}"

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; margin: 20px auto; }}
                .button {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                p {{ margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>您好 {username},</p>
                <p>感谢您注册【{settings.MAIL_FROM_NAME}】。请点击下面的按钮或链接以验证您的邮箱地址：</p>
                <p><a href="{verification_url}" class="button">验证邮箱地址</a></p>
                <p>如果按钮无法点击，请复制以下链接到您的浏览器地址栏中打开：<br>{verification_url}</p>
                <p>如果您没有在本网站注册账户，请忽略此邮件。</p>
                <p>此致，<br/>【{settings.MAIL_FROM_NAME}】团队</p>
            </div>
        </body>
    </html>
    """
    await send_email(subject=subject, recipients=[email_to], html_body=html_content)


# --- 新增：发送密码重置邮件的函数 ---
async def send_password_reset_email(email_to: EmailStr, username: str, token: str):
    """
    发送包含密码重置链接的邮件。
    """
    subject = f"{settings.MAIL_FROM_NAME} - 密码重置请求"
    # 构建密码重置链接，它应该指向前端的一个页面，该页面接收令牌并允许用户输入新密码
    # 例如：http://yourfrontend.com/reset-password?token=xxxxxxx
    reset_url = f"{settings.PORTAL_FRONTEND_BASE_URL}/reset-password?token={token}"

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; margin: 20px auto; }}
                .button {{ background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                p {{ margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>您好 {username},</p>
                <p>我们收到了一个重置您在【{settings.MAIL_FROM_NAME}】账户密码的请求。</p>
                <p>请点击下面的按钮或链接以设置您的新密码。如果您没有请求重置密码，请忽略此邮件。</p>
                <p><a href="{reset_url}" class="button">重置密码</a></p>
                <p>如果按钮无法点击，请复制以下链接到您的浏览器地址栏中打开：<br>{reset_url}</p>
                <p>此链接将在 {settings.PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS // 60} 分钟内有效。</p>
                <p>此致，<br/>【{settings.MAIL_FROM_NAME}】团队</p>
            </div>
        </body>
    </html>
    """
    await send_email(subject=subject, recipients=[email_to], html_body=html_content)
