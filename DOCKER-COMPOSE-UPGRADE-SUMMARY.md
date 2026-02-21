# Docker Compose v2 升级总结

## 升级概述

本次升级将项目从 Docker Compose v1 迁移到 v2，主要变化是命令语法从 `docker-compose`（下划线）改为 `docker compose`（横杠）。

## 已更新的文件

### 1. Docker Compose 配置文件

#### `docker-compose.yml` (开发环境)
- 移除了 `version: '3.8'` 字段（v2 中可选）
- 更新容器命名前缀为 `ems_sys-`
- 保持所有服务配置、健康检查和依赖关系不变

#### `docker-compose.prod.yml` (生产环境)
- 添加 `name: ems_sys` 项目名称
- 移除了 `version: '3.8'` 字段
- 更新容器命名前缀为 `ems_sys-`
- 更新镜像前缀为 `ems_sys`
- 保持所有资源限制和副本配置

### 2. 部署脚本

#### `scripts/deploy.sh`
- 所有 `docker-compose` 命令改为 `docker compose`
- 包括：pull, up, down, ps, logs, restart

#### `scripts/install-docker.sh`
- Docker Compose v2 安装为 CLI 插件
- 安装路径：`/usr/local/lib/docker/cli-plugins/docker-compose`
- 验证命令：`docker compose version`

### 3. 文档文件

#### `DEPLOYMENT-GUIDE.md`
- 所有 `docker-compose` 命令改为 `docker compose`
- 更新 Docker Compose 安装说明

#### `DEPLOYMENT-SUMMARY.md`
- 所有 `docker-compose` 命令改为 `docker compose`
- 更新安装步骤

#### `QUICK-DEPLOY.md`
- 所有 `docker-compose` 命令改为 `docker compose`
- 更新快速参考命令

#### `README.md`
- 添加 Docker Compose v2 说明注释
- 所有示例命令更新为 `docker compose`

#### `DOCKER-COMPOSE-V2.md` (新增)
- Docker Compose v2 完整升级指南
- 命令对照表
- 安装说明
- 故障排查

## 命令变化对照

| 场景 | v1 (已弃用) | v2 (推荐) |
|------|-----------|---------|
| 启动服务 | `docker-compose up -d` | `docker compose up -d` |
| 停止服务 | `docker-compose down` | `docker compose down` |
| 查看状态 | `docker-compose ps` | `docker compose ps` |
| 查看日志 | `docker-compose logs` | `docker compose logs` |
| 进入容器 | `docker-compose exec` | `docker compose exec` |
| 构建镜像 | `docker-compose build` | `docker compose build` |
| 重启服务 | `docker-compose restart` | `docker compose restart` |
| 指定文件 | `docker-compose -f xxx.yml` | `docker compose -f xxx.yml` |

## 安装方式变化

### v1 安装（已弃用）
```bash
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### v2 安装（推荐）
```bash
mkdir -p /usr/local/lib/docker/cli-plugins
curl -L "https://cdn.daocloud.io/docker-compose/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

## 向后兼容性

Docker Compose v2 仍然支持旧的 `docker-compose` 命令，但建议尽快迁移到新的 `docker compose` 语法。

## 验证升级

```bash
# 检查 Docker Compose 版本
docker compose version

# 预期输出
Docker Compose version v2.24.0
```

## 相关资源

- [Docker Compose v2 官方文档](https://docs.docker.com/compose/)
- [升级指南](DOCKER-COMPOSE-V2.md)
- [部署完整指南](DEPLOYMENT-GUIDE.md)
- [快速部署参考](QUICK-DEPLOY.md)

---

**升级完成时间**: 2026-02-21
**Docker Compose 版本**: v2.24.0
**项目名称**: EMS_SYS
