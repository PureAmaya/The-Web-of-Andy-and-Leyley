# 安迪和莉莉的门户 (The Portal of Andy and Leyley)

这是一个全栈 Web 应用，灵感来源于《安迪和莉莉的棺材》的独特艺术风格。项目后端采用 FastAPI，前端采用 Vue.js，旨在打造一个集作品展示、用户交互和社区功能于一体的门户网站。

## ✨ 功能特性 (Features)

-   **用户系统**：完整的用户注册、登录、邮件激活、密码重置流程。
-   **作品画廊**：支持用户上传图片作品，自动生成缩略图，分页展示，并提供灯箱预览和原图下载功能。
-   **后台管理**：基于 SQLAdmin 的强大后台管理面板，方便管理员管理用户、作品、成员、友情链接等数据。
-   **前端体验**：
    -   独特的复古、手绘风格 UI，支持日间/夜间模式切换。
    -   自托管字体和头像代理，优化国内网络环境下的访问速度和稳定性。
    -   动态友情链接和页脚备案信息展示。

## 🛠️ 技术栈与第三方库 (Tech Stack & Libraries)

#### 后端 (Backend)

-   **框架**: **FastAPI**
-   **数据库/ORM**: **PostgreSQL** + **SQLModel** & **SQLAlchemy**
-   **数据库迁移**: **Alembic**
-   **Web 服务器**: **Uvicorn**
-   **认证与安全**: **Passlib**, **python-jose**, **itsdangerous**
-   **后台面板**: **SQLAdmin**
-   **配置管理**: **pydantic-settings**
-   **图像处理**: **Pillow**
-   **HTTP 客户端**: **httpx**

#### 前端 (Frontend)

-   **框架**: **Vue 3**
-   **构建工具**: **Vite**
-   **状态管理**: **Pinia**
-   **路由**: **Vue Router**
-   **HTTP 客户端**: **axios**
-   **开发工具**: **Vite-plugin-vue-devtools**

## 🚀 部署指南 (Deployment Guide)

#### 准备工作
-   Git, Python 3.9+, Node.js 16+, PostgreSQL, Nginx

### 后端部署 (Backend)
1.  克隆仓库，创建并激活 Python 虚拟环境。
2.  安装依赖: `pip install -r requirements.txt`
3.  在项目根目录创建并配置 `.env` 文件（用于存放数据库、密钥等敏感信息）。
4.  运行数据库迁移: `alembic upgrade head`
5.  启动生产服务器: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app -b 0.0.0.0:8000`

### 前端部署 (Frontend)
1.  进入前端目录: `cd frontend`
2.  安装依赖: `npm install`
3.  **配置环境变量 (可选)**: 在 `frontend/` 目录下创建 `.env.production` 文件可指定生产环境的后端 API 地址 (如 `VITE_API_BASE_URL=https://api.yourdomain.com`)。
4.  **配置站点内容**: 检查并修改 `frontend/public/site-config.json` 文件（详见下一节）。
5.  构建项目: `npm run build`
6.  将 `frontend/dist` 目录下的所有文件上传到服务器，并使用 Nginx 等提供静态文件服务。

### 前端配置 (site-config.json)

为了方便地修改网站的公开信息而无需重新构建项目，本项目使用了一个位于 `frontend/public/site-config.json` 的配置文件。应用启动时会自动加载此文件。

它的结构如下：

```json
{
  "apiBaseUrl": "[http://127.0.0.1:8000](http://127.0.0.1:8000)",
  "contactInfo": {
    "email": "contact@yourdomain.com",
    "discord": "YourDiscordCommunity"
  },
  "beian": {
    "icp": "（请替换为您的ICP备案号）",
    "gongan": {
      "text": "（请替换为您的公安备案号）",
      "link": "（请替换为公安备案链接）"
    }
  }
}
````

  - `apiBaseUrl`: **(可选)** 可覆盖由 `.env` 文件设定的后端 API 地址。
  - `contactInfo`: 显示在网站上的联系方式。
  - `beian`: 网站的备案信息。如果 `icp` 字段为空字符串，备案信息将不会在页脚显示。

## ⚠️ 注意事项 (Important Notes)

  - **创建管理员账户**: 第一个管理员账户需要手动创建。注册一个普通用户后，直接在数据库中将其 `user` 表中对应记录的 `role` 字段从 `user` 修改为 `admin`。
  - **安全密钥**: `.env` 文件中的所有密钥和密码**必须**使用强随机字符串，并且**绝不能**提交到 Git 仓库。
  - **跨域配置 (CORS)**: 在生产环境中，请修改 `backend/main.py` 中的 `allow_origins` 列表，只允许您自己的前端域名访问。
  - **文件存储**: 目前用户上传的文件存储在服务器本地的 `backend/uploads/` 目录。对于生产环境，强烈建议改造为使用云存储服务。

## 📜 许可证 (License)

本项目代码采用 **Apache License 2.0** 许可证进行授权。详细信息请查看根目录下的 `LICENSE` 文件。

本项目中包含的字体文件（Noto Sans SC, Special Elite）使用 **SIL Open Font License 1.1** 许可证，其版权归原作者所有。

