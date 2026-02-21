# 运维手册

元器件商城系统生产环境运维指南。

---

## 目录

1. [系统架构](#系统架构)
2. [服务部署](#服务部署)
3. [日常运维](#日常运维)
4. [监控告警](#监控告警)
5. [备份恢复](#备份恢复)
6. [故障排查](#故障排查)
7. [应急预案](#应急预案)

---

## 系统架构

### 架构图

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (LB/SSL)   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  External   │ │  Internal   │ │    Admin    │
    │   Portal    │ │   Admin     │ │    Panel    │
    │  (Nuxt.js)  │ │  (Vue.js)   │ │   (Grafana) │
    └──────┬──────┘ └──────┬──────┘ └─────────────┘
           │               │
           └───────────────┼───────────────┐
                           │               │
                    ┌──────▼──────┐ ┌──────▼──────┐
                    │    API      │ │   Redis     │
                    │  (FastAPI)  │ │   Cache     │
                    └──────┬──────┘ └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    │  Database   │
                    └─────────────┘
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 80/443 | Web 服务器/SSL |
| External Portal | 3001 | 外部门户 |
| Internal Admin | 3000 | 内部管理 |
| API Gateway | 8001 | 后端 API |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Grafana | 3002 | 监控面板 |
| Prometheus | 9090 | 监控数据 |

---

## 服务部署

### Docker Compose 部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd claude-project

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量

# 3. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f

# 6. 停止服务
docker-compose down

# 7. 重启服务
docker-compose restart
```

### Kubernetes 部署

```bash
# 1. 创建命名空间
kubectl create namespace production

# 2. 创建配置
kubectl apply -k kubernetes/overlays/production

# 3. 验证部署
kubectl get pods -n production
kubectl get svc -n production

# 4. 查看日志
kubectl logs -f deployment/external-portal -n production

# 5. 扩容
kubectl scale deployment external-portal --replicas=5 -n production
```

---

## 日常运维

### 服务检查

```bash
# 检查 Docker 容器状态
docker ps -a

# 检查服务健康状态
docker inspect --format='{{.State.Health.Status}}' <container-name>

# 检查端口监听
netstat -tlnp | grep -E '(80|443|3000|3001|8001)'

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查 CPU 负载
top -bn1 | head -20
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f <service-name>

# 查看最近 100 行日志
docker-compose logs --tail=100 <service-name>

# 导出日志文件
docker-compose logs <service-name> > logs.txt

# 清理旧日志
docker-compose logs --tail=50 <service-name>
```

### 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 构建新镜像
docker-compose build

# 3. 重启服务
docker-compose up -d --force-recreate

# 4. 验证更新
docker-compose ps
curl https://your-domain.com/health
```

### 回滚操作

```bash
# Kubernetes 回滚
kubectl rollout undo deployment/external-portal -n production

# Docker 回滚（使用旧版本镜像）
docker-compose down
git checkout <previous-tag>
docker-compose up -d
```

---

## 监控告警

### Prometheus 监控指标

- **服务可用性**: HTTP 状态码、响应时间
- **资源使用**: CPU、内存、磁盘、网络
- **业务指标**: 订单量、用户活跃度、API 调用次数
- **数据库**: 连接数、查询延迟、慢查询

### Grafana 仪表板

访问地址：https://monitor.your-domain.com

预置仪表板：
- **系统概览**: CPU、内存、磁盘、网络
- **应用监控**: QPS、响应时间、错误率
- **数据库监控**: 连接数、查询性能
- **业务监控**: 订单趋势、用户活跃

### 告警规则

```yaml
# prometheus/rules/alerts.yml
groups:
  - name: system
    rules:
      - alert: HighCPU
        expr: avg(rate(container_cpu_usage_seconds_total[5m])) > 0.8
        for: 5m
        annotations:
          summary: "CPU 使用率过高"

      - alert: HighMemory
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        annotations:
          summary: "内存使用率过高"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        annotations:
          summary: "服务不可用"
```

### 告警通知

```yaml
# prometheus/config/alertmanager.yml
route:
  receiver: 'webhook'
  group_by: ['alertname']

receivers:
  - name: 'webhook'
    webhook_configs:
      - url: 'http://your-webhook-url/alert'

  - name: 'email'
    email_configs:
      - to: 'ops@example.com'
        from: 'alert@example.com'
        smarthost: 'smtp.example.com:587'
```

---

## 备份恢复

### 数据库备份

```bash
# 全量备份
pg_dump -h localhost -U admin ecs_db > backup_$(date +%Y%m%d).sql

# 压缩备份
pg_dump -h localhost -U admin ecs_db | gzip > backup_$(date +%Y%m%d).sql.gz

# 定时备份（crontab）
0 2 * * * pg_dump -h localhost -U admin ecs_db | gzip > /backup/ecs_$(date +\%Y\%m\%d).sql.gz
```

### 数据库恢复

```bash
# 恢复数据库
psql -h localhost -U admin ecs_db < backup_20260221.sql

# 恢复压缩备份
gunzip < backup_20260221.sql.gz | psql -h localhost -U admin ecs_db
```

### 配置文件备份

```bash
# 备份配置
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    docker-compose.prod.yml \
    .env \
    nginx.conf \
    kubernetes/

# 备份到远程
rsync -avz config_backup.tar.gz backup-server:/backups/
```

### 备份策略

| 数据类型 | 频率 | 保留期 | 存储位置 |
|---------|------|--------|---------|
| 数据库 | 每日 | 30 天 | 本地 + 远程 |
| 配置文件 | 每次变更 | 永久 | Git + 远程 |
| 日志文件 | 实时 | 90 天 | ELK Stack |
| 静态资源 | 实时 | 永久 | 对象存储 |

---

## 故障排查

### 常见问题

#### 1. 服务无法访问

```bash
# 检查服务状态
docker-compose ps

# 检查端口监听
netstat -tlnp | grep <port>

# 检查防火墙
ufw status

# 检查 Nginx 配置
nginx -t

# 查看服务日志
docker-compose logs <service-name>
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec postgres pg_isready

# 检查连接数
docker-compose exec postgres psql -U admin -c "SELECT count(*) FROM pg_stat_activity;"

# 重启数据库
docker-compose restart postgres
```

#### 3. 内存不足

```bash
# 查看内存使用
free -h
docker stats

# 清理未使用的镜像
docker image prune -a

# 重启占用内存高的服务
docker-compose restart <service-name>
```

#### 4. 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 Docker 资源
docker system prune -a

# 清理日志文件
> /var/log/docker/$(container-id)-json.log
```

### 性能问题

```bash
# 查看慢查询
docker-compose exec postgres psql -U admin -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 查看 API 延迟
# Grafana -> API Dashboard -> Response Time

# 查看数据库连接
docker-compose exec postgres psql -U admin -c "SELECT * FROM pg_stat_activity;"
```

---

## 应急预案

### 服务故障

1. **外部门户不可用**
   - 检查 Nginx 状态：`systemctl status nginx`
   - 重启服务：`docker-compose restart external-portal`
   - 查看日志：`docker-compose logs external-portal`
   - 切换备用服务（如有）

2. **数据库故障**
   - 检查主从状态
   - 切换到从库（如主库故障）
   - 从备份恢复数据

3. **SSL 证书过期**
   - 续期证书：`certbot renew`
   - 重载 Nginx：`systemctl reload nginx`

### 安全事件

1. **DDoS 攻击**
   - 启用 CDN 防护
   - 配置 Nginx 限流
   - 联系云服务商

2. **数据泄露**
   - 立即隔离受影响的服务
   - 修改所有密码和密钥
   - 审计访问日志
   - 通知相关方

### 联系方式

| 角色 | 联系人 | 电话 | 邮箱 |
|------|--------|------|------|
| 运维负责人 | 张三 | 138-xxxx-xxxx | ops@example.com |
| 开发负责人 | 李四 | 139-xxxx-xxxx | dev@example.com |
| 客服支持 | 王五 | 400-xxx-xxxx | support@example.com |

---

## 附录

### 常用命令速查

```bash
# Docker
docker-compose up -d              # 启动服务
docker-compose down               # 停止服务
docker-compose ps                 # 查看状态
docker-compose logs -f            # 查看日志
docker-compose restart <service>  # 重启服务

# Kubernetes
kubectl get pods                  # 查看 Pod
kubectl get svc                   # 查看服务
kubectl describe pod <name>       # Pod 详情
kubectl logs -f <pod>             # 查看日志
kubectl rollout status <deploy>   # 部署状态

# 系统
top                               # 进程监控
df -h                             # 磁盘使用
free -h                           # 内存使用
netstat -tlnp                     # 端口监听
```

---

**最后更新**: 2026-02-21
**版本**: 1.0.0
