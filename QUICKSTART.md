# 快速开始指南

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 内存
- 至少 20GB 可用磁盘空间

---

## 第一步：配置环境变量

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，修改以下关键配置：

```bash
# 数据库密码（必须修改）
POSTGRES_PASSWORD=your-super-secure-postgres-password-here

# Neo4j 配置（必须修改）
NEO4J_AUTH=neo4j/your-super-secure-neo4j-password-here
NEO4J_PASSWORD=your-super-secure-neo4j-password-here

# Redis 密码（必须修改）
REDIS_PASSWORD=your-super-secure-redis-password-here

# MinIO 配置（必须修改）
MINIO_ROOT_USER=your-minio-admin-user
MINIO_ROOT_PASSWORD=your-super-secure-minio-password-here

# JWT 密钥（必须修改，至少 32 字符）
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long-random-string

# AI 模型 API 密钥（可选）
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

### 生成安全密钥

**Linux/Mac:**
```bash
# PostgreSQL 密码
openssl rand -base64 32

# JWT 密钥
openssl rand -base64 48

# AES 加密密钥（正好 32 字符）
openssl rand -base64 32 | cut -c1-32
```

**Windows PowerShell:**
```powershell
# PostgreSQL 密码
[Convert]::ToBase64String((New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))

# JWT 密钥
[Convert]::ToBase64String((New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes(48))
```

---

## 第二步：启动所有服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志（实时）
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f order-service
docker-compose logs -f auth-service
```

---

## 第三步：访问服务

### 核心服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 内部管理系统 | http://localhost:3000 | Vue3 前端应用 |
| API 网关 (Nginx) | http://localhost:80 | 统一 API 入口 |
| Model Gateway | http://localhost:8000 | AI 模型网关 API |
| Auth Service | http://localhost:8001 | 用户认证服务 |
| Finance Service | http://localhost:8002 | 财务服务 |
| Inventory Service | http://localhost:8003 | 库存服务 |
| Order Service | http://localhost:8004 | 订单服务 |
| KG Service | http://localhost:8005 | 知识图谱服务 |

### 监控和日志

| 服务 | 地址 | 说明 |
|------|------|------|
| Grafana | http://localhost:3001 | 监控仪表板（admin/admin） |
| Prometheus | http://localhost:9090 | 监控数据 |
| Kibana | http://localhost:5601 | 日志分析 |
| MinIO Console | http://localhost:9001 | 对象存储管理 |

### 数据库

| 服务 | 地址 | 说明 |
|------|------|------|
| PostgreSQL | localhost:5432 | 关系数据库 |
| Neo4j Browser | http://localhost:7474 | 图数据库浏览器 |
| Neo4j Bolt | localhost:7687 | 图数据库连接 |
| Redis | localhost:6379 | 缓存数据库 |
| RabbitMQ | http://localhost:15672 | 消息队列管理（admin/admin123） |

---

## 第四步：测试 API

### 健康检查

```bash
# 检查所有服务健康状态
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### 用户注册和登录

```bash
# 用户注册
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123!",
    "email": "admin@example.com",
    "full_name": "系统管理员"
  }'

# 用户登录
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123!"
  }'
```

---

## 第五步：开发模式

### 前端开发

```bash
cd frontend/internal-admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test
```

### 后端开发

**Python 服务（FastAPI）:**
```bash
# Order Service
cd services/order-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004

# KG Service
cd services/kg-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005

# Model Gateway
cd services/model-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Go 服务:**
```bash
# Auth Service
cd services/auth-service
go run cmd/main.go

# Finance Service
cd services/finance-service
go run cmd/main.go

# Inventory Service
cd services/inventory-service
go run cmd/main.go
```

---

## 常见问题

### 1. 服务启动失败

```bash
# 检查 Docker 服务状态
docker-compose ps

# 查看详细日志
docker-compose logs -f

# 重启特定服务
docker-compose restart order-service

# 重建服务
docker-compose up -d --build order-service
```

### 2. 数据库连接失败

```bash
# 检查 PostgreSQL 健康状态
docker-compose exec postgres pg_isready

# 检查 Neo4j 健康状态
docker-compose exec neo4j cypher-shell -u neo4j -p your-password "RETURN 1"
```

### 3. 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8001:8001"  # 修改为其他端口，如 "8011:8001"
```

### 4. 内存不足

如果内存不足，修改 Neo4j 配置（在 `docker-compose.yml`）：
```yaml
neo4j:
  environment:
    NEO4J_dbms_memory_pagecache_size: "512M"  # 降低缓存
    NEO4J_dbms_memory_heap_max__size: "1G"    # 降低堆内存
```

---

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险操作！）
docker-compose down -v

# 停止并清理所有资源
docker-compose down --rmi all --volumes
```

---

## 下一步

1. **完成前端集成**: 继续 Phase 3 的前端页面业务逻辑集成
2. **开发外部门户**: 启动 Nuxt.js 外部门户开发
3. **性能优化**: 集成 Redis 缓存，优化数据库查询
4. **生产部署**: 配置 DMZ 区，部署 SSL 证书

---

**文档版本**: 1.0
**最后更新**: 2026-02-21
**项目版本**: 2.0.0 (Phase 2 完成)
