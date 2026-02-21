# 环境变量命名规范文档

## 统一环境变量命名约定

本文档定义了整个系统中使用的标准环境变量命名约定，确保所有服务使用一致的命名。

---

## 通用配置（所有服务）

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development`, `staging`, `production` |
| `DEBUG` | 调试模式 | `true`, `false` |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务监听端口 | `8000` |
| `LOG_LEVEL` | 日志级别 | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | 日志格式 | `json`, `text` |

---

## 数据库配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://user:pass@host:5432/dbname` |
| `DATABASE_POOL_SIZE` | 连接池大小 | `5` |
| `DATABASE_MAX_OVERFLOW` | 最大溢出连接数 | `10` |
| `DATABASE_POOL_TIMEOUT` | 连接池超时（秒） | `30` |
| `DATABASE_POOL_RECYCLE` | 连接回收时间（秒） | `3600` |

---

## Redis 配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `REDIS_URL` | Redis 连接字符串 | `redis://:password@host:6379/0` |

---

## 安全配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `JWT_SECRET` | JWT 签名密钥（至少 32 字符） | `your-secure-random-string...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 过期时间（分钟） | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 过期时间（天） | `7` |

---

## CORS 配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `CORS_ORIGINS` | 允许的跨域源（逗号分隔） | `http://localhost:3000,http://localhost:8080` |

---

## 对象存储（MinIO）配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `MINIO_ENDPOINT` | MinIO 服务端点 | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO 访问密钥 | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO 密钥 | `minioadmin` |
| `MINIO_BUCKET` | 默认存储桶 | `orders` |
| `MINIO_USE_SSL` | 是否使用 SSL | `false` |

---

## AI/LLM 配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | `sk-ant-...` |
| `LLM_MODEL` | 默认 LLM 模型 | `gpt-4` |
| `LLM_TEMPERATURE` | LLM 温度参数 | `0.1` |
| `LLM_MAX_TOKENS` | LLM 最大 Token 数 | `2000` |
| `LLM_TIMEOUT` | LLM 请求超时（秒） | `60` |

---

## OCR 配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `PADDLEOCR_ENDPOINT` | PaddleOCR 服务端点 | `http://localhost:8866` |
| `ALLOW_MOCK_OCR_DATA` | 是否允许模拟 OCR 数据（仅开发） | `false` |
| `OCR_TEMP_DIR` | OCR 临时目录 | `/tmp/ocr` |

---

## 服务间通信配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `AUTH_SERVICE_URL` | 认证服务地址 | `http://auth-service:8001` |
| `MODEL_GATEWAY_URL` | 模型网关地址 | `http://model-gateway:8000` |
| `ORDER_SERVICE_URL` | 订单服务地址 | `http://order-service:8004` |
| `FINANCE_SERVICE_URL` | 财务服务地址 | `http://finance-service:8002` |
| `INVENTORY_SERVICE_URL` | 库存服务地址 | `http://inventory-service:8003` |
| `KG_SERVICE_URL` | 知识图谱服务地址 | `http://kg-service:8005` |

---

## 消息队列配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `RABBITMQ_URL` | RabbitMQ 连接字符串 | `amqp://user:pass@host:5672/` |
| `RABBITMQ_EXCHANGE` | RabbitMQ 交换机名称 | `orders` |

---

## 前端配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | API 基础 URL（Vite） | `/api` |
| `VITE_USE_MOCK` | 是否使用 Mock 数据 | `false` |
| `VITE_APP_TITLE` | 应用标题 | `电子元器件代理商增值系统` |

---

## 最佳实践

1. **生产环境必须设置的变量**：
   - `DATABASE_URL`
   - `REDIS_URL`
   - `JWT_SECRET`（至少 32 字符）
   - `ENVIRONMENT=production`

2. **敏感信息**：
   - 所有密码、密钥必须通过环境变量或密钥管理系统注入
   - 不要在代码中硬编码任何敏感信息

3. **命名一致性**：
   - 使用大写字母和下划线（SCREAMING_SNAKE_CASE）
   - 相关配置使用相同前缀（如 `DATABASE_*`, `REDIS_*`）
