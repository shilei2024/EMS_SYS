# 变更日志 (CHANGELOG)

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [4.0.0] - 2026-02-21

### 新增 - Phase 4: 生产部署

#### 文档
- 新增 SSL 配置指南 (`docs/SSL-CONFIG.md`)
- 新增运维手册 (`docs/OPS-MANUAL.md`)
- 新增用户培训手册 (`docs/USER-TRAINING.md`)
- 新增 DMZ 区部署指南 (`docs/DMZ-DEPLOYMENT.md`)

#### SSL/HTTPS 配置
- Let's Encrypt 证书申请和自动续期
- Nginx HTTPS 配置优化
- HSTS、CSP 安全头配置
- OCSP Stapling 支持

#### 运维支持
- 服务部署（Docker Compose/Kubernetes）
- 日常运维命令速查
- 监控告警配置（Prometheus + Grafana）
- 备份恢复策略
- 故障排查指南
- 应急预案

#### 安全加固
- DMZ 区网络隔离
- 防火墙规则配置
- 容器安全加固
- 密钥管理（Vault）
- 审计日志

### 修改
- 更新 `README.md` - 更新 Phase 4 完成状态
- 更新版本号至 4.0.0

---

## [3.0.0] - 2026-02-21

### 新增 - Phase 3: 外部门户电商平台

#### 页面
- 新增首页 (`pages/index.vue`) - Hero 区域、产品分类、热门产品推荐
- 新增产品中心 (`pages/products.vue`) - 搜索、筛选、排序、分页
- 新增产品详情 (`pages/product/[id].vue`) - 图片展示、规格参数、Datasheet 下载
- 新增购物车 (`pages/cart.vue`) - 购物车管理、数量调整
- 新增订单中心 (`pages/orders.vue`) - 订单列表、详情、取消
- 新增个人中心 (`pages/profile.vue`) - 个人信息、密码修改
- 新增结账页面 (`pages/checkout.vue`) - 收货地址、支付方式、订单提交
- 新增关于我们 (`pages/about.vue`) - 公司介绍

#### 布局
- 新增默认布局 (`layouts/default.vue`) - 共享导航和底部

#### 组件
- 新增懒加载图片组件 (`components/LazyImage.vue`) - 图片懒加载、占位符
- 新增虚拟列表组件 (`components/VirtualList.vue`) - 大数据列表性能优化

#### 状态管理 (Pinia)
- 新增用户 Store (`stores/user.ts`) - 用户信息、登录状态
- 新增购物车 Store (`stores/cart.ts`) - 购物车 CRUD、本地降级

#### Composables
- 新增表单验证 (`composables/useFormValidation.ts`) - 用户名、密码、邮箱等验证

#### 工具模块
- 新增 API 客户端 (`utils/api.ts`) - axios 封装、JWT、CSRF、错误处理
- 新增安全工具 (`utils/security.ts`) - XSS 防护、密码验证、信息脱敏

#### API 集成
- 用户认证（登录/注册/登出）
- 用户信息获取
- 产品列表（分页、筛选、搜索）
- 产品详情
- 购物车管理（添加/更新/删除/清空）
- 订单管理（列表/详情/创建/取消）

#### 功能特性
- **首页**: Hero 区域、搜索框、统计数据、分类展示、热门产品
- **产品中心**: 分类筛选、品牌筛选、价格区间、关键词搜索、排序、分页
- **产品详情**: 图片展示、产品信息、价格库存、数量选择、加入购物车、立即购买、规格表、Datasheet 下载、相关产品推荐
- **购物车**: 列表展示、数量调整、删除商品、清空购物车、价格计算
- **结账页面**: 收货地址填写、支付方式选择、发票信息、订单备注、运费计算、订单提交
- **订单中心**: 订单列表、状态显示、订单详情、取消订单
- **个人中心**: 个人信息展示、编辑个人信息、修改密码、订单历史

#### 性能优化
- 代码分割（Vue/Vendor 分包）
- 路由懒加载
- 图片懒加载
- 虚拟滚动
- Gzip/Brotli 压缩
- 浏览器缓存（1 年）
- SSR/预渲染
- Nitro 压缩

#### 安全加固
- JWT Token 认证
- CSRF Token 支持
- XSS 防护（输入转义、HTML 清理）
- 密码强度验证
- 敏感信息脱敏
- 401/403 自动处理

#### 部署配置
- 新增外部门户 Dockerfile (`frontend/external-portal/Dockerfile`)
- 新增内部管理 Dockerfile (`frontend/internal-admin/Dockerfile`)
- 新增 Nginx 配置 (`frontend/internal-admin/nginx.conf`)
- 新增 Docker Compose 生产配置 (`docker-compose.prod.yml`)
- 新增 Kubernetes 部署配置 (`kubernetes/apps/external-portal.yaml`)
- 新增 GitLab CI/CD 流水线 (`.gitlab-ci.yml`)
- 新增部署指南文档 (`DEPLOYMENT.md`)
- 新增功能清单文档 (`FUNCTIONALITIES.md`)

### 修改

- 更新 `README.md` - 更新 Phase 3 完成状态
- 更新 `pages/products.vue` - 添加 LazyImage 组件、API 集成、跳转详情
- 更新 `pages/index.vue` - 添加 LazyImage 组件、API 集成、跳转详情
- 更新 `pages/cart.vue` - 修复产品字段名称
- 更新 `stores/cart.ts` - 添加 addItem 方法、本地降级处理
- 更新 `nuxt.config.ts` - 添加结账页面 SSR 配置

---

## [2.0.0] - 2026-02-XX

### 新增 - Phase 2: 订单自动化与 OCR 集成

#### 服务
- 订单服务 (`services/order-service`) - 订单处理、OCR 集成
- 知识图谱服务 (`services/kg-service`) - 元器件知识图谱
- 财务服务 (`services/finance-service`) - 财务管理
- 库存服务 (`services/inventory-service`) - 库存管理

#### 功能
- 多源订单接入（文件上传、API）
- OCR 结构化处理（PaddleOCR 集成）
- 订单审核工作流
- 知识图谱服务
- 财务报销流程
- 销售对账系统
- 库存预警系统
- FCST 需求预测

### 修改
- 更新内部管理系统前端
- 添加 WebSocket 实时通知
- 添加测试用例

---

## [1.0.0] - 2026-02-XX

### 新增 - Phase 1: 基础架构与核心服务

#### 服务
- 模型网关 (`services/model-gateway`) - 多 AI 提供商支持
- 认证服务 (`services/auth-service`) - JWT 认证、权限管理

#### 基础设施
- PostgreSQL 数据库配置
- Neo4j 图数据库配置
- Redis 缓存配置
- Prometheus + Grafana 监控
- ELK Stack 日志系统
- GitLab CI/CD 流水线

#### 功能
- JWT 认证
- 角色权限管理
- 会话控制
- 多 AI 提供商支持
- 主备自动切换
- 健康检查

---

## 版本说明

### Phase 1 (v1.0.0)
基础架构搭建，包含用户认证、模型网关等核心服务。

### Phase 2 (v2.0.0)
订单自动化处理，集成 OCR 和知识图谱服务。

### Phase 3 (v3.0.0)
外部门户电商平台，完整的前后端集成。

### Phase 4 (v4.0.0)
生产部署准备，包含 SSL 配置、运维手册、用户培训和安全加固。

---

## 贡献者

- 元器件商城系统团队

---

**[4.0.0]**: 2026-02-21 - Phase 4: 生产部署
**[3.0.0]**: 2026-02-21 - Phase 3: 外部门户电商平台
**[2.0.0]**: 2026-02-XX - Phase 2: 订单自动化与 OCR 集成
**[1.0.0]**: 2026-02-XX - Phase 1: 基础架构与核心服务
