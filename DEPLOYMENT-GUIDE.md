# 云服务器部署完整指南

本指南将帮助您将元器件商城系统完整部署到云服务器。

---

## 目录

1. [准备工作](#准备工作)
2. [GitHub 代码托管](#github 代码托管)
3. [云服务器准备](#云服务器准备)
4. [Docker 环境安装](#docker 环境安装)
5. [部署方式一：Docker Compose](#部署方式一-docker-compose)
6. [部署方式二：Kubernetes](#部署方式二 kubernetes)
7. [SSL/HTTPS 配置](#sslhttps 配置)
8. [CI/CD自动部署](#cicd 自动部署)
9. [运维监控](#运维监控)
10. [常见问题](#常见问题)

---

## 准备工作

### 1.1 系统要求

| 组件 | 要求 |
|------|------|
| 云服务器 | 4 核 CPU, 8GB 内存，50GB 硬盘（最低） |
| 推荐配置 | 8 核 CPU, 16GB 内存，100GB 硬盘 |
| 操作系统 | Ubuntu 20.04+ / CentOS 7+ |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

### 1.2 环境检查清单

- [ ] 云服务器已购买并完成初始化
- [ ] 域名已购买并完成 ICP 备案（中国大陆）
- [ ] GitHub 账号已注册
- [ ] SSH 密钥已配置

---

## GitHub 代码托管

### 2.1 创建 GitHub 仓库

```bash
# 1. 初始化本地 Git 仓库
cd D:\claude-project
git init

# 2. 添加所有文件
git add .

# 3. 创建初始提交
git commit -m "feat: initial commit - 元器件商城系统 v4.0.0"

# 4. 添加 GitHub 远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/EMS_SYS.git

# 5. 推送到 GitHub
git branch -M main
git push -u origin main
```

### 2.2 配置 .gitignore

项目已包含完善的 `.gitignore` 文件，确保敏感信息不会被提交：
- ✅ `.env` 环境变量文件
- ✅ `node_modules/` 依赖目录
- ✅ SSL 证书文件
- ✅ 数据库文件
- ✅ IDE 配置文件

### 2.3 创建 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下密钥：

| Secret Name | 说明 | 示例值 |
|------------|------|--------|
| `SERVER_HOST` | 服务器 IP 地址 | `123.45.67.89` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `DOCKER_USERNAME` | Docker Hub 用户名 | `your-docker-username` |
| `DOCKER_PASSWORD` | Docker Hub 密码/Access Token | `your-access-token` |
| `POSTGRES_PASSWORD` | PostgreSQL 密码 | `YourSecurePassword123!` |
| `JWT_SECRET` | JWT 密钥（至少 32 字符） | `your-random-jwt-secret-key` |
| `REDIS_PASSWORD` | Redis 密码 | `YourRedisPassword123!` |

---

## 云服务器准备

### 3.1 连接服务器

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 或配置 SSH 密钥免密登录
ssh-copy-id root@your-server-ip
```

### 3.2 系统更新

```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# CentOS/RHEL
yum update -y
```

### 3.3 安装必要工具

```bash
# Ubuntu/Debian
apt install -y curl git vim wget ufw

# CentOS/RHEL
yum install -y curl git vim wget firewalld
```

---

## Docker 环境安装

### ⚠️ 国内服务器重要提示

由于网络原因，建议使用国内镜像源安装 Docker。如遇 `Connection reset by peer` 错误，请使用备用方案。

### 4.1 方式一：使用国内镜像安装（推荐）

```bash
# 设置国内镜像源
export DOWNLOAD_URL=https://mirrors.aliyun.com/docker-ce

# 添加 Docker 仓库
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"

# 安装 Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
systemctl enable docker
systemctl start docker

# 验证安装
docker --version
```

### 4.2 方式二：使用 DaoCloud 镜像（备用）

```bash
# 使用 DaoCloud 镜像脚本
curl -sSL https://get.daocloud.io/docker | sh

# 或使用腾讯云镜像
curl -fsSL https://docker-installation.txstc55.workers.dev/install.sh | sh
```

### 4.3 方式三：手动下载安装（最终方案）

如果以上都失败，手动下载安装：

```bash
# 下载 Docker 二进制文件（使用国内镜像）
wget https://mirrors.aliyun.com/docker-ce/linux/static/stable/x86_64/docker-24.0.7.tgz

# 解压
tar -xzf docker-24.0.7.tgz
cp docker/* /usr/bin/

# 创建 systemd 服务
cat > /etc/systemd/system/docker.service <<EOF
[Unit]
Description=Docker Application Container Engine
After=network-online.target firewalld.service
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动 Docker
systemctl daemon-reload
systemctl enable docker
systemctl start docker

# 验证
docker --version
```

### 4.4 安装 Docker Compose

```bash
# 使用国内镜像下载 Docker Compose
curl -L "https://ghproxy.com/https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 或者使用 DaoCloud 镜像
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 4.5 配置 Docker 镜像加速（重要）

```bash
# 创建 Docker 配置目录
mkdir -p /etc/docker

# 配置国内镜像源
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://dhub.kubesre.xyz"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 重启 Docker
systemctl daemon-reload
systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

---

## 部署方式一：Docker Compose

### 5.1 克隆代码到服务器

> **注意**: 如果您在 GitHub 上使用了不同的仓库名称，请将 `EMS_SYS` 替换为您的实际仓库名称。克隆后的目录名称也会相应改变。

```bash
# 在服务器上执行
cd /opt
git clone https://github.com/YOUR_USERNAME/EMS_SYS.git
cd EMS_SYS
```

### 5.2 配置环境变量

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑环境变量（使用 vim 或 nano）
vim .env
```

**生产环境 .env 配置示例：**

```bash
# 数据库配置
POSTGRES_USER=component_admin
POSTGRES_DB=component_agent
POSTGRES_PASSWORD=YourSecurePostgresPassword123!

# Neo4j 配置
NEO4J_AUTH=neo4j/YourSecureNeo4jPassword123!
NEO4J_PASSWORD=YourSecureNeo4jPassword123!

# Redis 配置
REDIS_PASSWORD=YourSecureRedisPassword123!

# MinIO 配置
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=YourSecureMinioPassword123!

# JWT 配置
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long

# 加密密钥（必须正好 32 字符）
ENCRYPTION_AES_KEY=exactly-32-characters-long-key!!

# 运行环境
ENVIRONMENT=production

# CORS 配置（修改为您的实际域名）
CORS_ALLOW_ORIGINS=https://portal.your-domain.com,https://admin.your-domain.com
```

### 5.3 启动服务

```bash
# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止所有服务
docker compose -f docker-compose.prod.yml down
```

### 5.4 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 外部门户 | 3000 | Nuxt.js 电商平台 |
| 内部管理 | 3001 | Vue3 内部管理系统 |
| Nginx | 80/443 | API 网关和反向代理 |
| PostgreSQL | 5432 | 数据库（仅内网访问） |
| Redis | 6379 | 缓存（仅内网访问） |
| Model Gateway | 8000 | AI 模型网关 |
| Auth Service | 8001 | 认证服务 |
| Finance Service | 8002 | 财务服务 |
| Inventory Service | 8003 | 库存服务 |
| Order Service | 8004 | 订单服务 |
| KG Service | 8005 | 知识图谱服务 |
| Grafana | 3003 | 监控仪表板 |
| Prometheus | 9090 | 监控数据 |
| Kibana | 5601 | 日志分析 |

### 5.5 数据库初始化

```bash
# 查看数据库日志确认初始化成功
docker compose logs postgres

# 进入数据库验证
docker compose exec postgres psql -U postgres -d component_agent -c "\dt"
```

---

## 部署方式二：Kubernetes

### 6.1 安装 Kubernetes（可选）

```bash
# 安装 k3s（轻量级 K8s）
curl -sfL https://get.k3s.io | sh -

# 验证安装
kubectl get nodes
```

### 6.2 部署应用

```bash
cd /opt/EMS_SYS

# 应用 Kubernetes 配置
kubectl apply -k kubernetes/overlays/production

# 查看部署状态
kubectl get pods -n component-agent
kubectl get svc -n component-agent
```

---

## SSL/HTTPS 配置

### 7.1 申请 Let's Encrypt 证书

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 申请证书（确保域名已解析到服务器）
certbot --nginx -d portal.your-domain.com -d admin.your-domain.com

# 自动续期配置
certbot renew --dry-run
```

### 7.2 配置 Nginx HTTPS

编辑 `infrastructure/nginx/nginx.conf`：

```nginx
server {
    listen 80;
    server_name portal.your-domain.com admin.your-domain.com;

    # HTTP 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name portal.your-domain.com;

    ssl_certificate /etc/nginx/ssl/portal.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/portal.your-domain.com/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # 外部门户代理
    location / {
        proxy_pass http://external-portal:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name admin.your-domain.com;

    ssl_certificate /etc/nginx/ssl/admin.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/admin.your-domain.com/privkey.pem;

    # 相同 SSL 配置...

    # 内部管理代理
    location / {
        proxy_pass http://internal-admin:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 代理
    location /api/ {
        proxy_pass http://nginx:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7.3 防火墙配置

```bash
# Ubuntu UFW
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
ufw status

# CentOS Firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

---

## CI/CD 自动部署

### 8.1 GitHub Actions 配置

项目已包含 `.github/workflows/deploy.yml` 配置文件。

### 8.2 手动触发部署

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Deploy to Production**
4. 点击 **Run workflow**

### 8.3 自动部署

配置后，每次 push 到 main 分支会自动触发部署。

---

## 运维监控

### 9.1 访问监控仪表板

```bash
# Grafana (默认密码：admin)
http://your-server-ip:3003

# Prometheus
http://your-server-ip:9090

# Kibana
http://your-server-ip:5601
```

### 9.2 常用运维命令

```bash
# 查看所有服务状态
docker compose ps

# 重启单个服务
docker compose restart auth-service

# 查看服务日志
docker compose logs -f order-service

# 进入容器
docker compose exec postgres bash

# 数据库备份
docker compose exec postgres pg_dump -U postgres component_agent > backup.sql

# 数据库恢复
docker compose exec -T postgres psql -U postgres component_agent < backup.sql

# 清理无用镜像
docker image prune -f

# 查看磁盘使用
docker system df
```

### 9.3 日志管理

```bash
# 查看实时日志
docker compose logs -f

# 查看最近 100 行日志
docker compose logs --tail=100

# 导出日志到文件
docker compose logs > all-logs.txt
```

---

## 常见问题

### Q1: Docker 安装失败 - Connection reset by peer

**问题**: 国内访问 Docker 官方源网络问题

**解决方案**:

```bash
# 方案 1: 使用阿里云镜像
export DOWNLOAD_URL=https://mirrors.aliyun.com/docker-ce
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
apt update && apt install -y docker-ce

# 方案 2: 使用 DaoCloud 镜像
curl -sSL https://get.daocloud.io/docker | sh

# 方案 3: 手动下载
wget https://mirrors.aliyun.com/docker-ce/linux/static/stable/x86_64/docker-24.0.7.tgz
tar -xzf docker-24.0.7.tgz
cp docker/* /usr/bin/
```

### Q2: Docker Compose 下载失败

**问题**: GitHub 连接超时

**解决方案**:

```bash
# 使用国内镜像
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

### Q3: Docker 镜像拉取失败

**问题**: Docker Hub 连接超时

**解决方案**:

```bash
# 配置镜像加速
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF
systemctl restart docker
```

### Q4: 服务启动失败

```bash
# 查看详细日志
docker compose logs [service-name]

# 检查资源使用
docker stats

# 检查端口占用
netstat -tulpn | grep [port]
```

### Q5: 数据库连接失败

```bash
# 检查数据库是否运行
docker compose ps postgres

# 验证连接
docker compose exec postgres psql -U postgres -c "SELECT 1"

# 重启数据库
docker compose restart postgres
```

### Q6: 内存不足

```bash
# 限制服务内存（docker-compose.yml）
services:
  order-service:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Q7: SSL 证书续期

```bash
# 手动续期
certbot renew --force-renewal

# 配置自动续期（crontab）
0 3 * * * certbot renew --quiet
```

---

## 备份策略

### 数据库备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份 PostgreSQL
docker compose exec -T postgres pg_dump -U postgres component_agent | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份 Neo4j
docker compose exec -T neo4j neo4j-admin dump --to=/var/lib/neo4j/backups/neo4j_$DATE.dump

# 保留最近 7 天备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 定时备份任务

```bash
# 编辑 crontab
crontab -e

# 添加每日备份任务（每天凌晨 2 点）
0 2 * * * /opt/EMS_SYS/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 安全检查清单

- [ ] 修改所有默认密码
- [ ] 配置防火墙规则
- [ ] 启用 HTTPS/SSL
- [ ] 配置安全组（云服务商）
- [ ] 定期更新系统和 Docker
- [ ] 配置日志审计
- [ ] 定期备份数据
- [ ] 监控告警配置

---

## 联系支持

- **GitHub Issues**: https://github.com/YOUR_USERNAME/EMS_SYS/issues
- **技术文档**: `docs/` 目录
- **运维手册**: `docs/OPS-MANUAL.md`

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-21
