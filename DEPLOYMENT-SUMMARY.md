# 部署流程总结

本文档总结将元器件商城系统部署到云服务器的完整流程。

---

## 📋 部署清单

### 准备阶段

- [ ] 购买云服务器（推荐：4 核 8G 以上）
- [ ] 购买域名并完成 ICP 备案（中国大陆）
- [ ] 注册 GitHub 账号
- [ ] 注册 Docker Hub 账号

### 代码管理

- [ ] 初始化 Git 仓库
- [ ] 创建 GitHub 仓库
- [ ] 推送代码到 GitHub
- [ ] 配置 GitHub Secrets

### 服务器配置

- [ ] SSH 连接服务器
- [ ] 安装 Docker 和 Docker Compose（**使用国内镜像**）
- [ ] 配置 Docker 镜像加速
- [ ] 配置防火墙规则

### 应用部署

- [ ] 克隆代码到服务器
- [ ] 配置环境变量（.env）
- [ ] 启动 Docker 服务
- [ ] 验证服务运行状态

### SSL/HTTPS

- [ ] 配置域名 DNS 解析
- [ ] 申请 SSL 证书（Let's Encrypt）
- [ ] 配置 Nginx HTTPS
- [ ] 验证 HTTPS 访问

### 监控运维

- [ ] 访问 Grafana 监控面板
- [ ] 配置告警规则
- [ ] 设置日志保留策略
- [ ] 配置备份计划

---

## 🚀 快速部署命令

### ⚠️ 国内服务器重要提示

由于网络原因，请使用国内镜像源安装 Docker。

### 1. 快速安装 Docker（推荐）

```bash
# 方式 1: 使用 DaoCloud 镜像（最简单）
curl -fsSL https://get.daocloud.io/docker | sh

# 方式 2: 使用项目脚本
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/EMS_SYS/main/scripts/install-docker.sh | bash

# 方式 3: 使用阿里云镜像
export DOWNLOAD_URL=https://mirrors.aliyun.com/docker-ce
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
apt update && apt install -y docker-ce docker-ce-cli containerd.io
```

### 2. 安装 Docker Compose

```bash
# 使用国内镜像
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 验证安装
docker compose version
```

### 3. 配置 Docker 镜像加速

```bash
# 配置镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
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

### 4. 服务器初始化

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl git vim wget ufw

# 配置防火墙
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```
systemctl enable docker && systemctl start docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version && docker-compose --version
```

### 3. 部署应用

```bash
# 克隆代码
cd /opt
git clone https://github.com/YOUR_USERNAME/EMS_SYS.git
cd EMS_SYS

# 配置环境变量
cp .env.example .env
vim .env  # 编辑配置

# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 查看状态
docker compose ps
```

### 4. 配置 SSL

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
crontab -e
# 添加：0 3 * * * certbot renew --quiet
```

---

## 📁 文件结构

```
EMS_SYS/
├── .github/
│   ├── workflows/
│   │   ├── build.yml          # Docker 镜像构建
│   │   └── deploy.yml         # 自动部署
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml     # Bug 报告模板
│   │   └── feature_request.yml # 功能请求模板
│   └── environments/
│       └── production.yml     # 生产环境配置
├── scripts/
│   └── deploy.sh              # 一键部署脚本
├── frontend/
│   ├── external-portal/       # 外部门户
│   │   ├── Dockerfile
│   │   └── ...
│   └── internal-admin/        # 内部管理
│       ├── Dockerfile
│       └── ...
├── services/
│   ├── auth-service/          # 认证服务
│   ├── model-gateway/         # 模型网关
│   ├── order-service/         # 订单服务
│   ├── kg-service/            # 知识图谱
│   ├── finance-service/       # 财务服务
│   └── inventory-service/     # 库存服务
├── infrastructure/
│   ├── nginx/                 # Nginx 配置
│   ├── monitoring/            # 监控配置
│   └── logging/               # 日志配置
├── docs/
│   ├── SSL-CONFIG.md          # SSL 配置指南
│   ├── OPS-MANUAL.md          # 运维手册
│   ├── USER-TRAINING.md       # 用户培训
│   └── DMZ-DEPLOYMENT.md      # DMZ 部署
├── docker-compose.yml         # 开发环境
├── docker-compose.prod.yml    # 生产环境
├── DEPLOYMENT-GUIDE.md        # 完整部署指南
├── README.md                  # 项目说明
├── CONTRIBUTING.md            # 贡献指南
└── SECURITY.md                # 安全策略
```

---

## 🔐 环境变量配置

### 必填环境变量

```bash
# 数据库
POSTGRES_PASSWORD=你的 PostgreSQL 密码
POSTGRES_USER=postgres

# Neo4j
NEO4J_AUTH=neo4j/你的 Neo4j 密码
NEO4J_PASSWORD=你的 Neo4j 密码

# Redis
REDIS_PASSWORD=你的 Redis 密码

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=你的 MinIO 密码

# JWT
JWT_SECRET=至少 32 字符的随机字符串

# 加密
ENCRYPTION_AES_KEY=正好 32 字符的密钥
```

### 生成安全密钥

```bash
# JWT Secret (32+ 字符)
openssl rand -base64 32

# AES Key (正好 32 字符)
openssl rand -base64 32 | head -c 32

# 密码 (16 字符)
openssl rand -base64 12
```

---

## 🌐 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 80 | HTTP | Web 访问（重定向到 HTTPS） |
| 443 | HTTPS | 安全 Web 访问 |
| 3000 | 外部门户 | Nuxt.js 电商平台 |
| 3001 | 内部管理 | Vue3 管理系统 |
| 3003 | Grafana | 监控仪表板 |
| 5432 | PostgreSQL | 数据库（内网） |
| 6379 | Redis | 缓存（内网） |
| 8000-8005 | 微服务 | API 服务（内网） |
| 9090 | Prometheus | 监控数据 |
| 5601 | Kibana | 日志分析 |

---

## 🛠️ 常用运维命令

### 服务管理

```bash
# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 停止所有服务
docker compose -f docker-compose.prod.yml down

# 重启服务
docker compose restart

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs [service-name]
```

### 数据库管理

```bash
# 进入数据库
docker compose exec postgres psql -U postgres -d component_agent

# 备份数据库
docker compose exec postgres pg_dump -U postgres component_agent > backup.sql

# 恢复数据库
docker compose exec -T postgres psql -U postgres component_agent < backup.sql

# 查看数据库大小
docker compose exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('component_agent'));"
```

### 日志管理

```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f auth-service

# 导出日志
docker compose logs > logs.txt

# 清理日志
docker compose down -v
```

### 备份恢复

```bash
# 完整备份
tar -czf backup-$(date +%Y%m%d).tar.gz \
    postgres_data/ \
    neo4j_data/ \
    redis_data/ \
    minio_data/

# 恢复备份
tar -xzf backup-20260221.tar.gz
```

---

## 📊 监控告警

### Grafana 仪表板

访问 http://your-server-ip:3003

- 默认账号：admin / admin（首次登录请修改）

### 预配置仪表板

1. **系统监控**: CPU、内存、磁盘、网络
2. **服务监控**: 各微服务健康状态
3. **业务监控**: 订单量、用户数、API 调用

### 告警规则

```yaml
# Prometheus 告警规则
groups:
  - name: service_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        annotations:
          summary: "服务 {{ $labels.instance }} 已下线"

      - alert: HighCPU
        expr: rate(process_cpu_seconds_total[1m]) > 0.8
        for: 5m
        annotations:
          summary: "CPU 使用率超过 80%"
```

---

## 🔧 故障排查

### 常见问题

**Q1: 服务无法启动**

```bash
# 查看日志
docker compose logs [service-name]

# 检查端口占用
netstat -tulpn | grep [port]

# 检查资源
docker stats
```

**Q2: 数据库连接失败**

```bash
# 检查数据库状态
docker compose ps postgres

# 测试连接
docker compose exec postgres psql -U postgres -c "SELECT 1"
```

**Q3: 内存不足**

```bash
# 查看内存使用
free -h
docker stats

# 限制服务内存
# 在 docker-compose.prod.yml 中添加:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/YOUR_USERNAME/EMS_SYS/issues
- **技术文档**: `docs/` 目录
- **部署指南**: [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-21
