# 生产部署指南

本文档介绍如何将元器件商城系统部署到生产环境。

## 目录

1. [部署方式](#部署方式)
2. [Docker Compose 部署](#docker-compose-部署)
3. [Kubernetes 部署](#kubernetes-部署)
4. [CI/CD 部署](#cicd-部署)
5. [环境变量配置](#环境变量配置)
6. [性能优化](#性能优化)
7. [安全加固](#安全加固)
8. [监控与日志](#监控与日志)

---

## 部署方式

系统支持多种部署方式：

| 方式 | 适用场景 | 复杂度 |
|------|----------|--------|
| Docker Compose | 小型项目、单机部署 | ⭐⭐ |
| Kubernetes | 中大型项目、集群部署 | ⭐⭐⭐⭐ |
| 云服务器 | 快速部署、无需运维 | ⭐⭐ |

---

## Docker Compose 部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/your-org/ecs.git
cd ecs/frontend
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

3. **启动服务**
```bash
# 生产环境部署
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

4. **访问服务**
- 外部门户：http://localhost:3001
- 内部管理：http://localhost:3000

---

## Kubernetes 部署

### 前置要求

- Kubernetes 1.24+
- Helm 3.0+（可选）
- kubectl 配置完成

### 部署步骤

1. **创建命名空间**
```bash
kubectl create namespace production
```

2. **创建 ConfigMap**
```bash
kubectl create configmap app-config \
  --from-literal=apiBaseUrl=http://api-server:8001 \
  -n production
```

3. **创建 Secret**
```bash
kubectl create secret generic app-secrets \
  --from-literal=jwtSecret=your-secret-key \
  --from-literal=dbPassword=your-db-password \
  -n production
```

4. **部署应用**
```bash
# 部署外部门户
kubectl apply -f kubernetes/apps/external-portal.yaml -n production

# 部署内部管理
kubectl apply -f kubernetes/apps/internal-admin.yaml -n production
```

5. **验证部署**
```bash
kubectl get pods -n production
kubectl get svc -n production
```

---

## CI/CD 部署

### GitLab CI/CD

1. **配置 CI/CD 变量**
   - `DOCKER_REGISTRY`: Docker 镜像仓库地址
   - `DOCKER_USER`: Docker 仓库用户名
   - `DOCKER_PASSWORD`: Docker 仓库密码
   - `KUBE_CONFIG`: Kubernetes 配置（Base64 编码）
   - `K8S_CONTEXT`: Kubernetes 上下文名称
   - `API_BASE_URL`: API 基础地址

2. **推送代码**
   - 推送到 `develop` 分支自动部署到开发环境
   - 推送到 `main` 分支手动部署到生产环境

3. **查看部署状态**
   - 在 GitLab CI/CD 页面查看流水线状态
   - 查看部署日志

---

## 环境变量配置

### 外部门户 (.env)

```bash
# API 地址
NUXT_PUBLIC_API_BASE=http://localhost:8001

# 生产环境
NODE_ENV=production

# 日志级别
LOG_LEVEL=info
```

### 内部管理系统 (.env)

```bash
# API 地址
VITE_API_BASE=http://localhost:8001

# WebSocket 地址
VITE_WS_HOST=ws://localhost:8001
```

### 后端服务 (.env)

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=ecs_db

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password

# JWT 配置
JWT_SECRET=your-super-secret-key
JWT_EXPIRES_IN=7d

# API 密钥
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

---

## 性能优化

### 已配置优化

1. **代码分割**
   - Vue/Vendor 分包
   - Element Plus 分包
   - 路由懒加载

2. **静态资源优化**
   - Gzip/Brotli 压缩
   - 浏览器缓存（1 年）
   - 图片懒加载

3. **服务端优化**
   - SSR/预渲染
   - Nitro 压缩
   - 静态资源缓存

### 进一步优化建议

1. **CDN 加速**
   - 配置 CDN 域名
   - 将静态资源推送到 CDN

2. **数据库优化**
   - 添加索引
   - 查询优化
   - 读写分离

3. **缓存策略**
   - Redis 缓存热点数据
   - 页面缓存
   - API 响应缓存

---

## 安全加固

### 已实现安全措施

1. **XSS 防护**
   - 输入转义
   - 输出编码
   - CSP 策略（可选）

2. **CSRF 防护**
   - CSRF Token
   - SameSite Cookie

3. **输入验证**
   - 表单验证规则
   - 数据类型检查
   - 长度限制

### 建议加强的安全措施

1. **HTTPS 配置**
```bash
# 使用 Let's Encrypt 免费证书
certbot --nginx -d your-domain.com
```

2. **防火墙配置**
```bash
# 只开放必要端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

3. **数据库安全**
   - 修改默认端口
   - 限制远程访问
   - 定期备份

---

## 监控与日志

### Prometheus + Grafana 监控

1. **配置 Prometheus**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'external-portal'
    static_configs:
      - targets: ['external-portal:3000']
  - job_name: 'internal-admin'
    static_configs:
      - targets: ['internal-admin:80']
```

2. **Grafana 仪表板**
   - 导入 Node.js 应用监控模板
   - 配置告警规则

### 日志收集

1. **ELK Stack 配置**
```yaml
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

2. **日志级别配置**
```bash
# 生产环境建议配置
LOG_LEVEL=warn
```

---

## 故障排查

### 常见问题

1. **容器启动失败**
```bash
# 查看容器日志
docker-compose logs external-portal

# 进入容器调试
docker-compose exec external-portal sh
```

2. **Kubernetes Pod 无法启动**
```bash
# 查看 Pod 状态
kubectl describe pod <pod-name> -n production

# 查看 Pod 日志
kubectl logs <pod-name> -n production
```

3. **API 连接失败**
   - 检查 API 地址配置
   - 检查网络连接
   - 检查 CORS 配置

---

## 联系方式

如有问题，请联系：
- 技术支持：support@example.com
- 文档：https://docs.example.com
