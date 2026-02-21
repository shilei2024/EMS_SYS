# 电子元器件代理商增值系统

![版本](https://img.shields.io/badge/版本 -4.0.0-blue)
![状态](https://img.shields.io/badge/Phase-4 完成-green)
![许可](https://img.shields.io/badge/许可-MIT-green)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/component-agent/build.yml)

---

## 📖 项目概述

电子元器件代理商增值系统是一个基于微服务架构的企业级应用，旨在为电子元器件代理商提供智能化的订单处理、知识图谱管理、财务和库存管理等一站式解决方案。

| 系统 | 地址 | 说明 |
|------|------|------|
| 外部门户 | http://localhost:3000 | Nuxt.js 电商平台 |
| 内部管理 | http://localhost:3001 | Vue3 内部管理系统 |
| API 文档 | http://localhost:8000/docs | Swagger UI |

---

## 🚀 快速开始

### 一键部署（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/component-agent/main/scripts/deploy.sh | sudo bash
```

### Docker Compose 部署

```bash
git clone https://github.com/YOUR_USERNAME/component-agent.git
cd component-agent
cp .env.example .env
# 编辑 .env 文件配置环境变量
docker-compose -f docker-compose.prod.yml up -d
```

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 前端开发（外部门户）
cd frontend/external-portal && npm install && npm run dev

# 前端开发（内部管理）
cd frontend/internal-admin && npm install && npm run dev
```

---

## 核心功能

### Phase 1: 基础架构与核心服务 ✅
- 用户认证服务（Go + JWT）
- 模型网关服务（Python + LiteLLM）
- 数据库架构（PostgreSQL + Neo4j）
- 监控体系（Prometheus + Grafana）
- CI/CD 流水线

### Phase 2: 订单自动化与 OCR 集成 ✅
- 多源订单接入
- OCR 结构化处理（PaddleOCR）
- 订单审核工作流
- 知识图谱服务
- 财务报销流程
- 库存预警系统

### Phase 3: 系统集成与优化 ✅
- 外部门户（13 个页面）
- 状态管理（Pinia）
- 安全加固（JWT、CSRF、XSS 防护）
- 性能优化（代码分割、懒加载）

### Phase 4: 生产部署 ✅
- SSL/HTTPS 配置
- 运维手册
- 用户培训材料
- DMZ 区部署指南

---

## 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   模型网关      │    │   认证服务      │    │   订单服务      │
│   Python        │    │   Go           │    │   Python        │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         └──────────┬───────────┼──────────────────────┘
                    │           │
    ┌───────────────┼───────────┼──────────────────────┐
    │               │           │                      │
┌───▼───┐     ┌────▼────┐ ┌────▼────┐           ┌────▼────┐
│PostgreSQL│   │  Redis  │ │  Neo4j  │           │ MinIO   │
└─────────┘   └─────────┘ └─────────┘           └─────────┘
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Nuxt.js 3, Vue 3, TypeScript, Element Plus, Pinia |
| 后端 | Python FastAPI, Go Gin |
| 数据库 | PostgreSQL 15, Neo4j 5, Redis 7 |
| AI/OCR | PaddleOCR, LiteLLM |
| 基础设施 | Docker, Kubernetes, Nginx, MinIO |
| 监控 | Prometheus, Grafana, ELK Stack |

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) | 完整部署指南 |
| [docs/SSL-CONFIG.md](docs/SSL-CONFIG.md) | SSL/HTTPS 配置 |
| [docs/OPS-MANUAL.md](docs/OPS-MANUAL.md) | 运维手册 |
| [docs/USER-TRAINING.md](docs/USER-TRAINING.md) | 用户培训 |
| [docs/DMZ-DEPLOYMENT.md](docs/DMZ-DEPLOYMENT.md) | DMZ 部署指南 |

---

## 🏗️ 项目结构

```
component-agent/
├── services/                    # 微服务代码
│   ├── auth-service/           # Go 认证服务
│   ├── model-gateway/          # Python 模型网关
│   ├── order-service/          # 订单服务
│   ├── kg-service/             # 知识图谱服务
│   ├── finance-service/        # 财务服务
│   └── inventory-service/      # 库存服务
├── frontend/                   # 前端应用
│   ├── internal-admin/         # Vue3 内部管理系统
│   └── external-portal/        # Nuxt.js 外部门户
├── databases/                  # 数据库配置
├── infrastructure/             # 基础设施
├── kubernetes/                 # K8s 部署配置
├── scripts/                    # 部署脚本
├── docs/                       # 文档
└── docker-compose.yml          # Docker 编排
```

---

## 🔧 开发指南

### API 文档

访问 Swagger UI：
- Model Gateway: http://localhost:8000/docs
- Order Service: http://localhost:8004/docs
- KG Service: http://localhost:8005/docs

### 测试

```bash
# 后端测试
cd services/order-service && pytest -v --cov=app

# 前端测试
cd frontend/internal-admin && npm run test
```

---

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/YOUR_USERNAME/component-agent/issues
- **技术文档**: `docs/` 目录

---

**最后更新**: 2026-02-21
**版本**: 4.0.0 (Phase 4 完成 - 生产就绪)
