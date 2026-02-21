# 快速部署参考卡

## 🚀 一键部署命令

### 方式 1: 使用快速安装脚本（推荐）

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 安装 Docker 和 Docker Compose
curl -fsSL https://cdn.daocloud.io/docker | bash

# 或者使用项目脚本
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/EMS_SYS/main/scripts/install-docker.sh | bash
```

### 方式 2: 手动部署

```bash
# 1. 安装 Docker
export DOWNLOAD_URL=https://mirrors.aliyun.com/docker-ce
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
apt update && apt install -y docker-ce docker-ce-cli containerd.io

# 2. 安装 Docker Compose
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker compose/v2.24.0/docker compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker compose
chmod +x /usr/local/lib/docker/cli-plugins/docker compose

# 3. 配置镜像加速
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live"
  ]
}
EOF
systemctl daemon-reload && systemctl restart docker

# 4. 克隆并启动
cd /opt && git clone https://github.com/YOUR_USERNAME/EMS_SYS.git
cd EMS_SYS && cp .env.example .env
vim .env  # 编辑配置

# 5. 启动服务
docker compose -f docker compose.prod.yml up -d
```

---

## 📝 环境变量配置

```bash
# 生成安全密钥
JWT_SECRET=$(openssl rand -base64 32 | head -c 32)
REDIS_PASSWORD=$(openssl rand -base64 16 | head -c 16)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | head -c 24)

# 编辑 .env 文件
vim .env
```

---

## 🔍 验证部署

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 访问服务
# 外部门户：http://your-server-ip:3000
# 内部管理：http://your-server-ip:3001
# Grafana:   http://your-server-ip:3003
```

---

## 🛠️ 常用命令

```bash
# 启动服务
docker compose -f docker compose.prod.yml up -d

# 停止服务
docker compose -f docker compose.prod.yml down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f [service-name]

# 查看实时状态
watch -n 1 docker compose ps

# 数据库备份
docker compose exec postgres pg_dump -U postgres component_agent > backup.sql

# 清理空间
docker system prune -af
```

---

## 🔧 故障排查

### Docker 安装失败

```bash
# 使用 DaoCloud 镜像
curl -sSL https://get.daocloud.io/docker | sh

# 或手动下载
wget https://mirrors.aliyun.com/docker-ce/linux/static/stable/x86_64/docker-24.0.7.tgz
tar -xzf docker-24.0.7.tgz && cp docker/* /usr/bin/
```

### Docker Compose 下载失败

```bash
# 使用国内镜像
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker compose/v2.24.0/docker compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker compose
chmod +x /usr/local/lib/docker/cli-plugins/docker compose
```

### 镜像拉取失败

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

### 服务无法启动

```bash
# 查看详细日志
docker compose logs [service-name]

# 检查资源
docker stats
free -h
df -h

# 检查端口占用
netstat -tulpn | grep [port]
```

---

## 📦 端口列表

| 端口 | 服务 | 访问 |
|------|------|------|
| 80/443 | Nginx | 公网 |
| 3000 | 外部门户 | 公网 |
| 3001 | 内部管理 | 公网 |
| 3003 | Grafana | 公网 |
| 5432 | PostgreSQL | 内网 |
| 6379 | Redis | 内网 |
| 8000-8005 | 微服务 | 内网 |
| 9090 | Prometheus | 内网 |

---

## 🔐 安全配置

```bash
# 配置防火墙
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 配置 SSH（禁止 root 登录）
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# 修改默认密码
# Grafana: admin/admin → 首次登录修改
# PostgreSQL: 在 .env 中配置强密码
```

---

## 📚 完整文档

- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) - 完整部署指南
- [DEPLOYMENT-SUMMARY.md](DEPLOYMENT-SUMMARY.md) - 部署总结
- [docs/SSL-CONFIG.md](docs/SSL-CONFIG.md) - SSL 配置
- [docs/OPS-MANUAL.md](docs/OPS-MANUAL.md) - 运维手册

---

**版本**: 2.0.0
**更新**: 2026-02-21
**说明**: 添加国内镜像源，解决网络问题
