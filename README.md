<div align="center">
  <img src="docs/icon.png" alt="logo" width="128" height="128" />
  <h1 style="font-weight:700; letter-spacing:1px; margin-bottom:0;">
    安迪和莉莉的网站 (The Web of Andy and Leyley)
  </h1>
  <p>
    一个基于 Vue.js 和 FastAPI 构建的全栈社区门户网站，灵感来源于《安迪和莉莉的棺材》的独特艺术风格。
  </p>
  <p>
    <a href="https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley/releases"><img alt="Version" src="https://img.shields.io/github/v/release/PureAmaya/The-Web-of-Andy-and-Leyley?style=for-the-badge&logo=github"></a>
    <a href="https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/PureAmaya/The-Web-of-Andy-and-Leyley?style=for-the-badge"></a>
  </p>
</div>
*本项目与《安迪和莉莉的棺材》（The Coffin of Andy and Leyley）游戏本身无任何关联，为爱好者二次创作作品。*

---

## ✨ 功能特性 (Features)

<table width="100%">
  <thead>
    <tr>
      <th width="33%">用户体验 & 交互</th>
      <th width="33%">内容 & 社区管理</th>
      <th width="33%">管理与运维</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>✅ 完整的用户系统 (注册/登录/邮箱验证/密码重置)</td>
      <td>✅ 作品画廊 (图片/视频瀑布流展示)</td>
      <td>✅ <strong>图形化后台面板 (SQLAdmin)</strong></td>
    </tr>
    <tr>
      <td>✅ 响应式设计 (完美适配PC/移动端)</td>
      <td>✅ 灯箱式作品预览 (支持下载原文件)</td>
      <td>✅ 前端专属管理面板</td>
    </tr>
    <tr>
      <td>✅ 动态主题切换 (日间/夜间/跟随系统)</td>
      <td>✅ 成员信息展示与管理</td>
      <td>✅ <strong>配置热重载</strong> (无需重启服务)</td>
    </tr>
    <tr>
      <td>✅ 个人中心 (自定义头像/昵称/简介)</td>
      <td>✅ 友情链接管理</td>
      <td>✅ 可配置的用户注册开关</td>
    </tr>
    <tr>
      <td>✅ Minecraft 头像代理 (解决跨域问题)</td>
      <td>✅ 视频文件自动生成封面 (OpenCV)</td>
      <td>✅ 详细的日志与环境变量支持</td>
    </tr>
    <tr>
      <td>✅ 高性能异步API接口 (FastAPI)</td>
      <td>✅ 图片高质量缩略图生成 (Pillow)</td>
      <td>✅ 安全的JWT认证与密码哈希</td>
    </tr>
  </tbody>
</table>

## 🛠️ 技术栈 (Tech Stack)

<table width="100%">
  <thead>
    <tr>
      <th width="50%">后端 (Backend)</th>
      <th width="50%">前端 (Frontend)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <ul>
          <li><strong>框架</strong>: FastAPI</li>
          <li><strong>数据库/ORM</strong>: PostgreSQL + SQLModel & SQLAlchemy</li>
          <li><strong>数据库迁移</strong>: Alembic</li>
          <li><strong>后台管理</strong>: SQLAdmin</li>
          <li><strong>Web 服务器</strong>: Uvicorn</li>
          <li><strong>认证与安全</strong>: Passlib, python-jose, itsdangerous</li>
          <li><strong>图像/视频处理</strong>: Pillow, opencv-python-headless</li>
        </ul>
      </td>
      <td>
        <ul>
          <li><strong>框架</strong>: Vue 3 (Composition API & <code>&lt;script setup&gt;</code>)</li>
          <li><strong>构建工具</strong>: Vite</li>
          <li><strong>状态管理</strong>: Pinia</li>
          <li><strong>路由</strong>: Vue Router</li>
          <li><strong>UI 框架</strong>: Naive UI</li>
          <li><strong>HTTP 客户端</strong>: axios</li>
          <li><strong>开发工具</strong>: Vite-plugin-vue-devtools</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

## 🚀 快速开始


本指南将帮助您在本地计算机上完整地运行此项目，以进行开发和测试。

#### 准备工作

-   **Git**: 用于克隆代码仓库。
-   **Python 3.9+**: 后端运行环境。
-   **Node.js 16+ & npm**: 前端运行和构建环境。
-   **PostgreSQL**: 项目使用的数据库。请确保您已安装并能成功创建一个数据库。

#### 后端本地启动

1.  **克隆仓库并进入项目**
    ```bash
    git clone https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley
    cd The-Web-of-Andy-and-Leyley
    ```
2.  **创建并激活 Python 虚拟环境**
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows: venv\Scripts\activate
    ```
3.  **安装后端依赖**
    
    ```bash
    pip install -r requirements.txt
    ```
4.  **配置本地数据库与环境变量**
    -   启动 PostgreSQL 服务并创建一个新的数据库 (例如 `minecraft_web_db`) 和一个有权限的用户。
    -   在项目根目录下，创建一个名为 `.env` 的文件，复制下方模板内容，并根据您的本地配置修改（当文件不存在时，程序也会自动创建）。
    ```env
    # PostgreSQL 数据库配置
    POSTGRES_USER=your_local_db_user
    POSTGRES_PASSWORD=your_local_db_password
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=minecraft_web_db
    
    # JWT 和其他安全令牌的密钥 (必须填写随机字符串)
    SESSION_SECRET_KEY=...
    JWT_SECRET_KEY=...
    JWT_REFRESH_SECRET_KEY=...
    JWT_ALGORITHM=...
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7
    PASSWORD_RESET_SECRET_KEY=...
    PASSWORD_RESET_SALT=...
    PASSWORD_RESET_TOKEN_MAX_AGE_SECONDS=900
    EMAIL_VERIFICATION_SECRET_KEY=...
    EMAIL_VERIFICATION_SALT=...
    
    
    # 邮件服务配置
    MAIL_USERNAME=...
    MAIL_PASSWORD=...
    MAIL_FROM=...
    MAIL_SERVER=...
    MAIL_PORT=465
    MAIL_STARTTLS=False
    MAIL_SSL_TLS=True
    MAIL_FROM_NAME=...
    
    # 前端 URL (用于生成邮件中的链接)
    PORTAL_FRONTEND_BASE_URL=http://localhost:5173
    
    # 是否开启用户注册 (true: 开启, false: 关闭)
    ENABLE_REGISTRATION=true
    
    # CORS 允许的前端源列表，用逗号分隔
    CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
    
    # 文件上传配置
    UPLOAD_ALLOWED_MIME_TYPES="image/jpeg,image/png,image/gif,video/mp4"
    UPLOAD_MAX_SIZE_MB=50
    
    # 画廊分页配置
    GALLERY_DEFAULT_PAGE_SIZE=12
    GALLERY_MAX_PAGE_SIZE=100
    
    # Minecraft 头像服务模板 (用 {username} 作为占位符)
    MC_AVATAR_URL_TEMPLATE="https://cravatar.eu/avatar/{username}/128.png"
    ```
5.  **应用数据库迁移**
    ```bash
    alembic upgrade head
    ```
6.  **启动后端开发服务器**
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    - 后端 API 将运行在 `http://127.0.0.1:8000`。

#### 前端本地启动

1.  **进入前端目录并安装依赖** (请打开一个新的终端窗口)
    ```bash
    cd frontend
    npm install
    ```
2.  **启动前端开发服务器**
    ```bash
    npm run dev
    ```
    - 在浏览器中打开命令行提示的地址（通常是 `http://localhost:5173`）即可。

<details>
<summary><strong>► 点击展开/折叠 生产环境部署指南 (Production Deployment Guide)</strong></summary>

本指南以 **Ubuntu 22.04** 为例，引导您完成应用的完整部署。

#### 阶段一：服务器准备与环境安装

1.  **更新系统并安装核心依赖**
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y git python3-pip python3-venv nginx postgresql postgresql-contrib curl
    ```
2.  **安装 Node.js (v18+)**
    ```bash
    curl -fsSL [https://deb.nodesource.com/setup_18.x](https://deb.nodesource.com/setup_18.x) | sudo -E bash -
    sudo apt install -y nodejs
    ```
3.  **配置防火墙**
    ```bash
    sudo ufw allow 'OpenSSH'
    sudo ufw allow 'Nginx Full'
    sudo ufw enable
    ```

#### 阶段二：数据库与后端应用部署

1.  **创建数据库和用户** (在`psql`中执行)
    ```sql
    CREATE DATABASE minecraft_web_db;
    CREATE USER your_db_user WITH PASSWORD 'your_secure_password';
    GRANT ALL PRIVILEGES ON DATABASE minecraft_web_db TO your_db_user;
    \q
    ```
2.  **克隆代码并设置Python环境**
    ```bash
    git clone [https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley.git](https://github.com/PureAmaya/The-Web-of-Andy-and-Leyley.git)
    cd The-Web-of-Andy-and-Leyley
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install uvicorn gunicorn # 生产环境建议使用 gunicorn
    ```
3.  **配置生产环境变量**
    在项目根目录创建并编辑 `.env` 文件，填入您的生产配置（数据库、密钥、域名等）。**确保关闭注册 `ENABLE_REGISTRATION=false` 并设置正确的 `CORS_ALLOWED_ORIGINS`**。

4.  **应用数据库迁移**
    ```bash
    alembic upgrade head
    ```

5.  **使用 `systemd` 管理后端服务**
    - 创建服务文件 `sudo nano /etc/systemd/system/my_webapp.service`。
    - **请务必将所有 `/path/to/your/project` 替换为您项目的实际绝对路径**。
    ```ini
    [Unit]
    Description=Gunicorn instance to serve my_webapp
    After=network.target
    
    [Service]
    User=your_server_user # 运行服务的用户名
    Group=www-data
    WorkingDirectory=/path/to/your/project/The-Web-of-Andy-and-Leyley
    Environment="PATH=/path/to/your/project/The-Web-of-Andy-and-Leyley/venv/bin"
    ExecStart=/path/to/your/project/The-Web-of-Andy-and-Leyley/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 backend.main:app
    
    [Install]
    WantedBy=multi-user.target
    ```
    - 启动并启用服务：
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start my_webapp
    sudo systemctl enable my_webapp
    ```

#### 阶段三：前端构建与 Nginx 配置

1.  **构建前端静态文件**
    ```bash
    cd frontend
    npm install
    npm run build
    ```
2.  **配置 Nginx 反向代理**
    - 创建 Nginx 配置文件 `sudo nano /etc/nginx/sites-available/your_domain.com`。
    - 粘贴以下配置，这是根据您提供的配置优化而来，**请替换 `your_domain.com` 和路径**。
    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name your_domain.com;
    
        # 用于 Let's Encrypt 证书续签验证
        location ~ /.well-known/acme-challenge {
            allow all;
            root /var/www/html;
        }
    
        # 将所有 HTTP 请求强制重定向到 HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name your_domain.com;
    
        # SSL 证书路径 (使用 Certbot 获取后会自动配置)
        # ssl_certificate /path/to/fullchain.pem;
        # ssl_certificate_key /path/to/privkey.pem;
        # include /etc/letsencrypt/options-ssl-nginx.conf;
        # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
        # 前端静态文件根目录
        root /path/to/your/project/The-Web-of-Andy-and-Leyley/frontend/dist;
        index index.html;
    
        # 日志文件
        access_log /var/log/nginx/your_domain.com.access.log;
        error_log /var/log/nginx/your_domain.com.error.log;
    
        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        
        # 代理到后端的 API 请求
        location /api/ {
            client_max_body_size 50M; # 必须大于等于 .env 中的 UPLOAD_MAX_SIZE_MB
            proxy_pass [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/); # 注意这里的斜杠
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    
        # 核心：处理 Vue Router 的 History 模式
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
    ```
    - 启用配置:
    ```bash
    sudo ln -s /etc/nginx/sites-available/your_domain.com /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    ```

#### 阶段四：配置 HTTPS (Certbot)

1.  **安装 Certbot**
    ```bash
    sudo apt install certbot python3-certbot-nginx
    ```
2.  **获取并安装证书**
    Certbot 会自动修改您的 Nginx 配置以启用 HTTPS。
    ```bash
    sudo certbot --nginx -d your_domain.com
    ```
    部署完成！

## 🔑 项目管理与首次配置

### ⚠️ **重要：创建您的第一个管理员账户**

**本项目的设计非常巧妙：第一个成功注册的用户将自动被赋予管理员（admin）权限。**

因此，首次部署的流程如下：

1.  **确保注册功能已开启**: 在您的 `.env` 文件中，确保 `ENABLE_REGISTRATION=true`。
2.  **部署并启动应用**: 按照上方指南完成部署。
3.  **立即注册**: 访问您的网站，**成为第一个注册的用户**。这个账户将是您唯一的初始管理员账户。
4.  **（强烈建议）关闭后续注册**: 注册成功后，为了安全起见，立即修改 `.env` 文件，设置 `ENABLE_REGISTRATION=false`，然后通过 `管理面板` 重载环境。这样可以防止其他人注册为普通用户。

现在，您可以使用第一个注册的账户凭据登录，并管理整个网站了。


## 📜 许可证 (License)

本项目代码采用 **Apache License 2.0** 许可证。详细信息请查看 `LICENSE` 文件。

字体文件 (Noto Sans SC, Special Elite) 使用 **SIL Open Font License 1.1** 许可证。

## 🤝 致谢 (Acknowledgements)

本项目的开发过程得到了 **Google Gemini 2.5 Pro 模型** 的辅助，在代码实现、功能优化和文档撰写等方面提供了诸多有益的建议。
