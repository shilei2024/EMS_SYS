# 电子元器件代理商增值系统部署指南

## Phase 1: 基础架构与核心服务

### 系统概述

电子元器件代理商增值系统是一个基于微服务架构的企业级应用，包含以下核心服务：

1. **模型网关服务** (model-gateway) - Python FastAPI，大模型统一接口
2. **认证服务** (auth-service) - Go，用户管理和JWT认证
3. **数据库集群** - PostgreSQL, Neo4j, Redis
4. **监控系统** - Prometheus, Grafana, 告警规则

### 环境要求

#### 硬件要求
- CPU: 8核以上
- 内存: 16GB以上
- 存储: 100GB SSD以上

#### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- (可选) Kubernetes 1.24+
- Git

### 快速开始（开发环境）

#### 1. 克隆代码库
```bash
git clone <repository-url>
cd claude-project
```

#### 2. 配置环境变量
创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键变量：
```env
# 数据库密码（生产环境必须修改）
POSTGRES_PASSWORD=your_strong_password_here
NEO4J_AUTH=neo4j/your_strong_password_here
REDIS_PASSWORD=your_strong_password_here

# JWT密钥（必须修改）
JWT_SECRET=your_32_character_long_jwt_secret_key_here

# AI服务API密钥
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 环境配置
ENVIRONMENT=development
DEBUG=true
```

#### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 初始化数据库
```bash
# 数据库会自动通过init-scripts初始化
# 手动验证数据库
docker exec -it component-agent-postgres psql -U postgres -d component_agent -c "\dt"
```

#### 5. 访问服务
- **模型网关API**: http://localhost:8000/docs
- **认证服务API**: http://localhost:8001/api/v1/health
- **Grafana监控**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **MinIO控制台**: http://localhost:9001 (minioadmin/minioadmin)
- **RabbitMQ管理**: http://localhost:15672 (admin/admin123)

### 生产环境部署

#### Kubernetes部署（推荐）

##### 1. 准备Kubernetes集群
```bash
# 创建命名空间
kubectl create namespace component-agent

# 创建配置映射
kubectl apply -f kubernetes/config/

# 创建Secrets（从安全存储加载）
kubectl create secret generic database-secrets \
  --from-literal=postgres-password='your_password' \
  --from-literal=redis-password='your_password' \
  --namespace component-agent

kubectl create secret generic jwt-secret \
  --from-literal=jwt-secret='your_jwt_secret' \
  --namespace component-agent

kubectl create secret generic api-keys \
  --from-literal=openai-api-key='your_key' \
  --from-literal=anthropic-api-key='your_key' \
  --namespace component-agent
```

##### 2. 部署数据库
```bash
# 部署PostgreSQL
kubectl apply -f kubernetes/databases/postgres/

# 部署Redis
kubectl apply -f kubernetes/databases/redis/

# 部署Neo4j
kubectl apply -f kubernetes/databases/neo4j/
```

##### 3. 部署应用服务
```bash
# 部署模型网关
kubectl apply -f kubernetes/services/model-gateway/

# 部署认证服务
kubectl apply -f kubernetes/services/auth-service/

# 部署Ingress
kubectl apply -f kubernetes/ingress/
```

##### 4. 部署监控
```bash
# 部署Prometheus
kubectl apply -f kubernetes/monitoring/prometheus/

# 部署Grafana
kubectl apply -f kubernetes/monitoring/grafana/

# 部署告警管理器
kubectl apply -f kubernetes/monitoring/alertmanager/
```

#### 健康检查
```bash
# 检查所有Pod状态
kubectl get pods -n component-agent

# 检查服务端点
kubectl get svc -n component-agent

# 检查Ingress
kubectl get ingress -n component-agent

# 手动健康检查
curl https://api.your-domain.com/health
curl https://api.your-domain.com/api/v1/health
```

### 安全配置

#### 1. 网络隔离
```yaml
# kubernetes/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-isolation
  namespace: component-agent
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
```

#### 2. TLS/SSL配置
```bash
# 使用cert-manager自动管理证书
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# 创建ClusterIssuer
kubectl apply -f kubernetes/tls/cluster-issuer.yaml

# 创建Certificate
kubectl apply -f kubernetes/tls/certificate.yaml
```

#### 3. 安全上下文
```yaml
# 容器安全上下文示例
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  seccompProfile:
    type: RuntimeDefault
```

### 监控和告警

#### 1. 关键指标监控
- **服务可用性**: HTTP状态码、响应时间
- **资源使用**: CPU、内存、磁盘、网络
- **业务指标**: 订单处理量、OCR成功率、模型调用次数
- **安全指标**: 登录失败次数、API调用频率

#### 2. 告警配置
告警规则已预配置在 `infrastructure/monitoring/prometheus/alerts.yml` 中，包含：

- **基础设施告警**: 高CPU/内存使用率、磁盘空间不足
- **服务告警**: 服务不可用、高错误率、高延迟
- **业务告警**: 订单积压、OCR失败率高
- **安全告警**: 异常登录尝试、暴力破解攻击

#### 3. 告警通知渠道
- Email
- Slack
- Webhook
- PagerDuty
- 企业微信/钉钉

### 备份和恢复

#### 1. 数据库备份
```bash
# PostgreSQL备份
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec component-agent-postgres pg_dump -U postgres component_agent > $BACKUP_DIR/backup_$DATE.sql

# 上传到云存储
gsutil cp $BACKUP_DIR/backup_$DATE.sql gs://your-backup-bucket/
```

#### 2. 配置文件备份
```bash
# 备份所有配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  infrastructure/ \
  databases/init-scripts/
```

#### 3. 恢复流程
```bash
# PostgreSQL恢复
docker exec -i component-agent-postgres psql -U postgres component_agent < backup_file.sql

# 配置文件恢复
tar -xzf config_backup.tar.gz
cp .env.production .env
docker-compose up -d
```

### 故障排除

#### 常见问题

##### 1. 服务启动失败
```bash
# 检查日志
docker-compose logs [service-name]

# 检查端口冲突
netstat -tulpn | grep :8000

# 检查依赖服务
docker-compose ps
```

##### 2. 数据库连接问题
```bash
# 测试PostgreSQL连接
docker exec component-agent-postgres pg_isready -U postgres

# 测试Redis连接
docker exec component-agent-redis redis-cli -a your_password ping
```

##### 3. API调用失败
```bash
# 检查服务健康
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/health

# 检查网络连通性
docker-compose exec model-gateway curl http://auth-service:8001/health
```

##### 4. 监控数据缺失
```bash
# 检查Prometheus目标
curl http://localhost:9090/api/v1/targets

# 检查指标端点
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics
```

### 升级指南

#### 1. 版本升级
```bash
# 拉取最新代码
git pull origin main

# 重建镜像
docker-compose build --no-cache

# 重启服务
docker-compose down
docker-compose up -d --force-recreate

# 运行数据库迁移
docker exec component-agent-postgres psql -U postgres -d component_agent -f /docker-entrypoint-initdb.d/02-migration.sql
```

#### 2. 回滚流程
```bash
# 回滚到上一个版本
git checkout <previous-tag>

# 重启服务
docker-compose down
docker-compose up -d

# 恢复数据库备份（如果需要）
docker exec -i component-agent-postgres psql -U postgres component_agent < backup_before_upgrade.sql
```

### 性能调优

#### 1. 数据库调优
```sql
-- PostgreSQL性能优化
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

#### 2. 服务调优
```yaml
# docker-compose.override.yml
services:
  model-gateway:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
        reservations:
          memory: 1G
          cpus: '0.5'
```

#### 3. 缓存策略
- Redis缓存热点数据
- 数据库查询结果缓存
- 静态资源CDN加速

### 附录

#### A. 默认账户
- **Grafana**: admin/admin
- **MinIO**: minioadmin/minioadmin
- **RabbitMQ**: admin/admin123
- **系统管理员**: admin/Admin@12345 (首次登录后必须修改)

#### B. 端口映射
| 服务 | 端口 | 协议 | 用途 |
|------|------|------|------|
| 模型网关 | 8000 | HTTP | API服务 |
| 认证服务 | 8001 | HTTP | 认证API |
| PostgreSQL | 5432 | TCP | 数据库 |
| Redis | 6379 | TCP | 缓存 |
| Neo4j HTTP | 7474 | HTTP | 图数据库UI |
| Neo4j Bolt | 7687 | TCP | 图数据库协议 |
| Prometheus | 9090 | HTTP | 监控 |
| Grafana | 3000 | HTTP | 可视化 |
| MinIO API | 9000 | HTTP | 对象存储 |
| MinIO Console | 9001 | HTTP | 管理界面 |

#### C. 环境变量参考
完整的环境变量列表请参考 `config/.env.example` 文件。

#### D. 技术支持
- 文档: docs/
- 问题跟踪: GitHub Issues
- 紧急联系: ops@your-company.com
- SLA: 99.9% 可用性

---

**最后更新**: 2026-02-21
**版本**: 1.0.0
**作者**: 电子元器件代理商增值系统团队