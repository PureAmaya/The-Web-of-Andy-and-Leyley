# <img src="docs/icon.png" style="zoom:2%;" /> 安迪和莉莉的网站 (The Web of Andy and Leyley)

这是一个全栈 Web 应用，灵感来源于《安迪和莉莉的棺材》（The Coffin of Andy and Leyley）的独特艺术风格。项目后端采用 FastAPI，前端采用 Vue.js，旨在打造一个集作品展示、用户交互和社区功能于一体的门户网站。

*本项目与 `《安迪和莉莉的棺材》（The Coffin of Andy and Leyley）` 没有任何联系*，为第三方二次创作作品。



## 🌟 项目亮点 (Project Highlights)

- **现代技术栈**: 采用 FastAPI + Vue 3 的前后端分离架构，兼具开发效率与高性能。
- **风格化UI**: 实现了独特的复古艺术风格，支持日间/夜间/跟随系统的三模主题一键切换，并内置了配套的自托管字体。
- **配置驱动**: 网站标题、联系方式、备案信息、首页标语等内容均可通过JSON文件轻松配置，无需修改代码。
- **完整的用户系统**: 提供从注册、邮件验证、登录、密码重置到个人主页展示的全套用户认证和管理流程。
- **高级画廊功能**: 不仅是图片陈列，更提供了独特的卡片悬浮交互、作品详情灯箱预览和原图下载功能。
- **全面的后台管理**: 集成 SQLAdmin，让管理员可以通过图形化界面轻松管理用户、作品、成员和友情链接等核心数据。
- **网络优化**: 内置 Minecraft 头像代理，解决了前端直接请求外部资源可能存在的网络问题，确保头像稳定显示。

## ✨ 功能清单 (Feature List)

#### 🔧 后端 (Backend)

- **RESTful API**: 基于 FastAPI 构建的清晰、高效的 API 接口。

- 用户认证:

  - 完整的 JWT (JSON Web Token) 认证流程，包含访问令牌和刷新令牌。
  - 安全的密码哈希存储 (Passlib)。
  - 基于邮件的**账户激活**验证流程。
  - 完整的**忘记密码/密码重置**流程。
  
- 动态配置:

  - 支持通过环境变量 (`.env`) 动态开启或关闭用户注册功能。
  - 提供公共配置接口，使前端能同步后端的开关状态。
  
- 文件处理:

  - 健壮的图片上传接口，支持文件类型和大小校验。
  - 使用 Pillow 自动为上传的图片生成高质量缩略图。
  
- **代理服务**: 内置 Minecraft 头像代理接口 (`/avatars/mc/{username}`), 解决前端跨域问题。

- **数据库**: 使用 SQLModel 进行数据建模，并通过 Alembic 管理数据库结构迁移。

- **性能优化**: 对数据库查询采用预先加载（Eager Loading），解决 N+1 问题，提升画廊等页面的加载性能。

#### 🖥️ 前端 (Frontend)

- **响应式布局**: 界面在桌面和移动设备上均有良好表现，并优化了宽屏显示，内容可占满全屏。

- **状态管理**: 使用 Pinia 集中管理用户认证、站点配置等全局状态。

- **API 客户端**: 通过集中的 Axios 实例 (`api.js`) 管理所有 API 请求，并使用拦截器自动处理认证头和401错误。

- **动态主题**: 支持**日间/夜间/跟随系统**的三模主题切换，颜色和风格完全自定义。

- 高级画廊:

  - 图片卡片拥有独特的旋转悬浮交互效果，信息按需展示。
  - 支持分页浏览所有作品。
  - 灯箱预览模式下，支持查看创作者、上传者等详细信息，并提供**下载原图**功能。
  
- 内容配置化:

  - 首页标题、联系方式、页脚版权、备案信息等内容均可通过 `public/site-config.json` 进行配置。
- 备案信息在配置为空时会自动隐藏，无需修改代码。

#### 🔑 管理与运维 (Admin & Operations)

- **后台管理面板**: 集成了 SQLAdmin，为管理员提供了一个功能齐全的图形化界面，可直接在后台对**用户、作品、成员、友情链接**等所有数据模型进行增删改查操作。
- **生产级部署**: 提供了基于 Gunicorn + Uvicorn (后端) 和 Nginx (前端) 的完整生产环境部署方案。

## 🛠️ 技术栈与第三方库 (Tech Stack & Libraries)

#### 后端 (Backend)

- **框架**: **FastAPI**
- **数据库/ORM**: **PostgreSQL** + **SQLModel** & **SQLAlchemy**
- **数据库迁移**: **Alembic**
- **Web 服务器**: **Uvicorn**
- **认证与安全**: **Passlib**, **python-jose**, **itsdangerous**
- **后台面板**: **SQLAdmin**
- **配置管理**: **pydantic-settings**
- **图像处理**: **Pillow**
- **HTTP 客户端**: **httpx**

#### 前端 (Frontend)

- **框架**: **Vue 3** (Composition API & `<script setup>`)
- **构建工具**: **Vite**
- **状态管理**: **Pinia**
- **路由**: **Vue Router**
- **HTTP 客户端**: **axios**
- **开发工具**: **Vite-plugin-vue-devtools**

## 🚀 本地开发指南 (Local Development Guide)

本指南将帮助您在本地计算机上完整地运行此项目，以进行开发和测试。

#### 准备工作

- **Git**: 用于克隆代码仓库。
- **Python 3.9+**: 后端运行环境。
- **Node.js 16+ & npm**: 前端运行和构建环境。
- **PostgreSQL**: 项目使用的数据库。请确保您已安装并能成功创建一个数据库。

### 后端本地启动

1. **克隆仓库并进入项目**

   ```
   git clone https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley
   cd The-Web-of-Andy-and-Leyley-main
   ```
   
2. **创建并激活 Python 虚拟环境**

   ```
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```
   
3. **安装后端依赖**

   ```
   pip install -r requirements.txt
   ```
   
4. **配置本地数据库**

   - 启动您的 PostgreSQL 服务。
   - 创建一个新的数据库，例如命名为 `minecraft_web_db`。
   - 创建一个新的数据库用户（或使用现有用户），并确保该用户拥有对新数据库的所有权限。

5. **配置本地环境变量**

   - 在项目根目录下，创建一个名为 `.env` 的文件。
   - 复制下方模板内容到 `.env` 文件中，并根据您的本地数据库配置进行修改。密钥部分可以使用 `openssl rand -hex 32` 等工具生成随机字符串。

   ```
   # .env (本地开发示例)
   POSTGRES_USER=your_local_db_user
   POSTGRES_PASSWORD=your_local_db_password
   POSTGRES_SERVER=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=minecraft_web_db
   ENABLE_REGISTRATION=true # 本地开发时通常开启注册
   
   # JWT 和其他安全令牌的密钥 (必须填写)
   JWT_SECRET_KEY=...
   JWT_REFRESH_SECRET_KEY=...
   EMAIL_VERIFICATION_SECRET_KEY=...
   EMAIL_VERIFICATION_SALT=...
   PASSWORD_RESET_SECRET_KEY=...
   PASSWORD_RESET_SALT=...
   
   # 邮件服务配置 (用于注册验证和密码重置，可使用临时邮箱服务测试)
   MAIL_USERNAME=...
   MAIL_PASSWORD=...
   MAIL_FROM=...
   MAIL_PORT=587
   MAIL_SERVER=...
   MAIL_FROM_NAME=安迪和莉莉的门户(开发版)
   
   # 前端 URL (用于生成邮件中的链接)
   PORTAL_FRONTEND_BASE_URL=http://localhost:5173
   ```
   
6. 应用数据库迁移

   此命令会根据 alembic/versions 目录下的迁移文件，在您的数据库中创建所有需要的表。

   Bash

   ```
   alembic upgrade head
   ```

7. **启动后端开发服务器**

   Bash

   ```
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - `--reload` 参数会使服务器在代码变更时自动重启，非常适合开发。
   - 现在，您的后端 API 应该已在 `http://127.0.0.1:8000` 上运行。

### 前端本地启动

1. **进入前端目录并安装依赖** (请打开一个新的终端窗口)

   ```
   cd frontend
   npm install
   ```
   
2. **启动前端开发服务器**

   ```
   npm run dev
   ```
   
   - 此命令会启动一个带热重载的前端开发服务器。
- 在浏览器中打开命令行提示的地址（通常是 `http://localhost:5173`），即可看到您的网站。

## 🚀 部署指南 (Deployment Guide)

### 准备工作

- 一台已配置好防火墙的云服务器（例如 Ubuntu 22.04）。
- Git, Python, Node.js, PostgreSQL, Nginx。

### 后端部署

1. 启动生产服务器

   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app -b 0.0.0.0:8000
   ```
   
   - `-w 4`: 启动 4 个 worker 进程 (可根据 CPU 核心数调整)。
   - `-k uvicorn.workers.UvicornWorker`: 指定使用 uvicorn 作为 worker 类。
   - `-b 0.0.0.0:8000`: 绑定到 8000 端口。 *建议使用 `systemd` 将此命令作为后台服务来管理。*

### 前端部署

1. 配置 Nginx

   ```
   server {
       listen 80;
       server_name yourdomain.com; # 替换为您的域名
       root /path/to/your/frontend/dist; # 指向前端构建文件的路径
       index index.html;
   
       # 应对 Vue Router 的 History 模式
       location / {
           try_files $uri $uri/ /index.html;
       }
   
       # 将所有 /api/ 的请求反向代理到后端 FastAPI 服务
       location /api/ {
           client_max_body_size 10M; # 允许最大10MB的上传文件
           proxy_pass http://127.0.0.1:8000/; # 注意末尾的斜杠
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## 🔑 项目管理指南 (Management Guide)

### 访问后台管理面板

- **URL**: 在浏览器中访问 `https://yourdomain.com/admin` (或本地开发的 `http://127.0.0.1:8000/admin`)。
- **登录**: 使用您创建的管理员账户的用户名和密码登录。

### 创建您的第一个管理员账户

本项目不会自动创建管理员。您需要手动提升一个已注册用户的权限：

1. **正常注册**: 在网站上（确保注册功能已开启）注册一个新用户。

2. **登录数据库**: 使用 `psql` 或 pgAdmin 等工具连接到您的 PostgreSQL 数据库。

3. 执行 SQL 命令: 

   找到 ` user` 表，并更新您刚刚注册的用户的 `role` 字段。


   ```
   UPDATE "user" SET role = 'admin' WHERE username = 'your_registered_username';
   ```

4. **完成**: 现在，您可以使用这个用户的凭据登录后台管理面板了。

### 可管理内容

通过后台管理面板，您可以直观地进行以下操作：

- **用户管理**: 查看、编辑、禁用或删除用户。
- **画廊管理**: 发布、修改或下架画廊作品。
- **成员管理**: 编辑服务器的核心成员信息。
- **友链管理**: 添加或删除页脚的友情链接。

## ⚙️ 配置文件说明 (Configuration Explained)

本项目使用两种配置文件来分离不同类型的设置：

1. **`.env` (后端/敏感信息)**
   - **位置**: 项目根目录。
   - **用途**: 存放敏感信息和与环境相关的配置，如数据库凭据、API密钥、JWT密钥等。
   - **注意**: **此文件绝不能提交到 Git 仓库**。
2. **`frontend/public/site-config.json` (前端/公开信息)**
   - **位置**: `frontend/public/` 目录下。
   - **用途**: 存放可以公开的、与网站内容相关的配置，如**首页标语**、联系方式、页脚版权、备案信息等。修改此文件**无需重新构建**前端项目，刷新浏览器即可看到变化。

## ⚠️ 注意事项 (Important Notes)

- **创建管理员账户**: 见上文管理指南。
- **安全密钥**: `.env` 文件中的所有密钥**必须**使用强随机字符串。
- **跨域配置 (CORS)**: 在生产环境中，请修改 `backend/main.py` 中的 `allow_origins` 列表，只允许您自己的前端域名访问。
- **文件存储**: 目前为本地存储。生产环境建议改造为使用云存储服务。

## 📜 许可证 (License)

本项目代码采用 **Apache License 2.0** 许可证进行授权。详细信息请查看根目录下的 `LICENSE` 文件。

本项目中包含的字体文件（Noto Sans SC, Special Elite）使用 **SIL Open Font License 1.1** 许可证，其版权归原作者所有。

## 🤝 致谢 (Acknowledgements)

本项目的开发过程得到了 **Google Gemini  2M5 Pro模型**的辅助，在代码实现、功能优化和文档撰写等方面提供了诸多有益的建议。
