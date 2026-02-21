# Docker Compose v2 升级指南

## 📋 概述

本项目已升级到 Docker Compose v2，使用新的命令语法 `docker compose`（横杠格式）替代了旧的 `docker-compose`（下划线格式）。

## 🔄 主要变化

### 命令语法变化

| Docker Compose v1 (已弃用) | Docker Compose v2 (推荐) |
|--------------------------|------------------------|
| `docker-compose up -d` | `docker compose up -d` |
| `docker-compose down` | `docker compose down` |
| `docker-compose ps` | `docker compose ps` |
| `docker-compose logs` | `docker compose logs` |
| `docker-compose exec` | `docker compose exec` |
| `docker-compose build` | `docker compose build` |
| `docker-compose -f docker-compose.yml` | `docker compose -f docker-compose.yml` |

### 安装方式变化

**v1 安装方式（已弃用）**:
```bash
# 下载到 /usr/local/bin/
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

**v2 安装方式（推荐）**:
```bash
# 作为 Docker CLI 插件安装
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

### Docker Compose 文件变化

#### v1 格式
```yaml
version: '3.8'  # 需要 version 字段

services:
  app:
    image: myapp:latest
```

#### v2 格式
```yaml
# version 字段已弃用（可选）
# 可以使用 name 字段定义项目名称

name: myproject

services:
  app:
    image: myapp:latest
```

## 🚀 快速开始

### 开发环境
```bash
# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 生产环境
```bash
# 使用生产配置启动
docker compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 停止服务
docker compose -f docker-compose.prod.yml down
```

## 📦 常用命令参考

### 服务管理
```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 删除服务
docker compose down

# 重新构建并启动
docker compose up -d --build

# 强制重新创建容器
docker compose up -d --force-recreate
```

### 日志和调试
```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f [service-name]

# 查看最近 100 行日志
docker compose logs --tail=100

# 进入容器
docker compose exec [service-name] bash

# 运行容器内命令
docker compose exec [service-name] [command]
```

### 数据库操作
```bash
# 进入数据库
docker compose exec postgres psql -U postgres -d component_agent

# 备份数据库
docker compose exec postgres pg_dump -U postgres component_agent > backup.sql

# 恢复数据库
docker compose exec -T postgres psql -U postgres component_agent < backup.sql
```

## 🔧 故障排查

### 常见问题

**Q1: `docker compose` 命令不存在**

确保 Docker Compose v2 已正确安装为 CLI 插件：
```bash
# 检查安装
docker compose version

# 如果失败，重新安装
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

**Q2: 旧脚本仍然使用 `docker-compose`**

更新脚本中的命令：
```bash
# 旧命令
docker-compose -f docker-compose.prod.yml up -d

# 新命令
docker compose -f docker-compose.prod.yml up -d
```

**Q3: 项目名称变化**

v2 使用目录名作为默认项目名称，可以使用 `--project-name` 指定：
```bash
docker compose --project-name ems_sys up -d
```

或在 docker-compose.yml 中定义：
```yaml
name: ems_sys
```

## 📚 相关文档

- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) - 完整部署指南
- [DEPLOYMENT-SUMMARY.md](DEPLOYMENT-SUMMARY.md) - 部署总结
- [QUICK-DEPLOY.md](QUICK-DEPLOY.md) - 快速部署参考
- [Docker Compose 官方文档](https://docs.docker.com/compose/)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-21
**Docker Compose 版本**: v2.24.0
