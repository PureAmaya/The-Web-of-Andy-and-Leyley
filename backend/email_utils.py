# 文件: backend/email_utils.py

import smtplib
import ssl
from email.message import EmailMessage
from pydantic import EmailStr
import logging

# 导入您的应用配置
from backend.core.config import get_settings

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)

async def send_email(subject: str, recipients: list[EmailStr], html_body: str):
    """
    通用的邮件发送函数，使用 smtplib 实现。
    """
    # 从配置中获取邮件服务器信息
    settings = get_settings()
    smtp_server = settings.MAIL_SERVER
    port = settings.MAIL_PORT
    username = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD
    sender_email = settings.MAIL_FROM

    # 创建 EmailMessage 对象
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"{settings.MAIL_FROM_NAME} <{sender_email}>"
    msg['To'] = ", ".join(recipients)
    # 设置邮件内容为 HTML 格式
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html_body, 'utf-8')

    logger.info(f"准备在后台任务中发送邮件至 {recipients}...")
    try:
        # 完全复用您成功的测试脚本逻辑
        if port == 587:
            with smtplib.SMTP(smtp_server, port, timeout=15) as server:
                server.set_debuglevel(1)  # 打印详细交互日志
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
        elif port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context, timeout=15) as server:
                server.set_debuglevel(1)  # 打印详细交互日志
                server.login(username, password)
                server.send_message(msg)
        else:
            logger.error(f"不支持的邮件端口: {port}。")
            return

        logger.info(f"后台邮件任务成功发送至: {recipients}")
    except Exception as e:
        logger.error("!!!!!! 后台邮件任务发送失败 !!!!!!")
        logger.exception(e)  # 打印完整的错误堆栈


async def send_verification_email(email_to: EmailStr, username: str, token: str):
    """
    发送包含验证链接的邮件给新注册用户。
    (此函数内容保持不变，因为它调用的是通用的 send_email 函数)
    """
    settings = get_settings()
    subject = f"{settings.MAIL_FROM_NAME} - 邮箱验证"
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


async def send_password_reset_email(email_to: EmailStr, username: str, token: str):
    """
    发送包含密码重置链接的邮件。
    (此函数内容也保持不变)
    """
    settings = get_settings()
    subject = f"{settings.MAIL_FROM_NAME} - 密码重置请求"
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