# 外部门户 (External Portal)

基于 Nuxt.js 3 的外部门户网站，为电子元器件商城提供面向客户的 Web 界面。

## 技术栈

- **框架**: Nuxt.js 3
- **前端**: Vue 3 + TypeScript
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios

## 快速开始

### 安装依赖

```bash
cd frontend/external-portal
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3001

### 构建生产版本

```bash
npm run build
npm run preview
```

## 项目结构

```
external-portal/
├── app.vue                 # 应用入口
├── nuxt.config.ts          # Nuxt 配置
├── package.json            # 项目依赖
├── tsconfig.json           # TypeScript 配置
├── pages/                  # 页面组件
│   ├── index.vue          # 首页
│   ├── products.vue       # 产品中心
│   ├── login.vue          # 用户登录
│   └── about.vue          # 关于我们
├── components/             # 可复用组件
├── composables/            # Composables
├── stores/                 # Pinia 状态管理
├── utils/                  # 工具函数
└── public/                 # 静态资源
```

## 页面列表

| 页面 | 路由 | 状态 |
|------|------|------|
| 首页 | `/` | ✅ 已完成 |
| 产品中心 | `/products` | ✅ 已完成 |
| 关于我们 | `/about` | ✅ 已完成 |
| 联系我们 | `/contact` | 📋 待开发 |
| 用户登录 | `/login` | ✅ 已完成 |
| 用户注册 | `/register` | 📋 待开发 |
| 购物车 | `/cart` | 📋 待开发 |
| 订单中心 | `/orders` | 📋 待开发 |
| 个人中心 | `/profile` | 📋 待开发 |

## 待开发功能

### 高优先级 (P0)

1. **联系我们页面** - 联系方式、在线留言
2. **用户注册页面** - 注册表单、邮箱验证
3. **产品详情页** - 产品参数、Datasheet 下载

### 中优先级 (P1)

4. **购物车功能** - 添加/删除、数量调整
5. **订单中心** - 订单列表、订单详情、订单跟踪
6. **个人中心** - 个人信息、密码修改、收货地址

### 低优先级 (P2)

7. **搜索功能增强** - 模糊搜索、热门搜索
8. **收藏功能** - 产品收藏、收藏列表
9. **评价系统** - 产品评价、评价列表

## 环境变量

```bash
# .env 文件
NUXT_PUBLIC_API_BASE=http://localhost:8001
```

## SEO 优化

- 服务端渲染 (SSR)
- 页面预渲染 (Prerendering)
- Meta 标签动态生成
- Sitemap 自动生成

## 下一步

1. 完成剩余页面开发
2. 集成后端 API
3. 实现用户认证
4. 添加支付功能
5. 部署到生产环境
