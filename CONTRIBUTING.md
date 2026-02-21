# 贡献者指南

感谢您对元器件商城系统的关注！本指南将帮助您参与项目贡献。

## 开发环境设置

### 1. Fork 和克隆

```bash
# 1. 在 GitHub 上 Fork 项目
# 2. 克隆您的 Fork
git clone https://github.com/YOUR_USERNAME/EMS_SYS.git
cd EMS_SYS

# 3. 添加上游仓库
git remote add upstream https://github.com/YOUR_USERNAME/EMS_SYS.git
```

### 2. 配置环境

```bash
# 复制环境变量
cp .env.example .env

# 编辑 .env 文件，配置必要的变量
```

### 3. 启动开发环境

```bash
# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 或者只启动前端
cd frontend/external-portal
npm install
npm run dev
```

## 提交代码

### Git 工作流

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature-name

# 2. 进行更改并提交
git add .
git commit -m "feat: add your feature description"

# 3. 推送到分支
git push origin feature/your-feature-name

# 4. 在 GitHub 上创建 Pull Request
```

### 提交消息格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>: <description>

[optional body]
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat: add user profile page

- Add user information display
- Add password change functionality
- Add order history view

Closes #123
```

## 代码规范

### 前端代码

- 使用 ESLint 和 Prettier 进行代码格式化
- 遵循 Vue 3 组合式 API 风格
- TypeScript 严格模式

```bash
# 运行代码检查
npm run lint

# 自动格式化
npm run format
```

### 后端代码

**Python:**
- 遵循 PEP 8
- 使用 Black 格式化

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行格式化
black .
```

**Go:**
- 使用 `gofmt`
- 遵循 Go 代码规范

```bash
# 格式化代码
gofmt -w .

# 运行 vet
go vet ./...
```

## 测试

### 运行测试

```bash
# 后端测试
cd services/order-service
pytest -v --cov=app

# 前端测试
cd frontend/internal-admin
npm run test
```

### 测试覆盖要求

- 单元测试：80%+
- 关键业务逻辑：必须覆盖
- API 端点：必须覆盖

## 提交 PR

### PR 检查清单

在创建 Pull Request 之前，请确保：

- [ ] 代码已通过 ESLint/PEP8 检查
- [ ] 测试已通过
- [ ] 提交了更新文档
- [ ] 更新了 CHANGELOG.md

### PR 标题格式

```
<type>: <short description>
```

**示例：**
```
feat: add product search functionality
fix: resolve user authentication issue
docs: update deployment guide
```

## 代码审查

所有 PR 都需要经过代码审查。审查者将关注：

1. 代码质量和规范
2. 功能正确性
3. 测试覆盖
4. 文档完整性
5. 性能影响

## 问题反馈

### 报告 Bug

使用 [GitHub Issues](https://github.com/YOUR_USERNAME/EMS_SYS/issues) 报告 Bug。

**Bug 报告模板：**

```markdown
### 问题描述
简要描述问题

### 复现步骤
1. 步骤一
2. 步骤二

### 期望行为
应该发生什么

### 实际行为
实际发生了什么

### 环境信息
- OS:
- Node.js:
- 其他：
```

### 功能请求

使用 GitHub Issues 提出功能请求。

**功能请求模板：**

```markdown
### 功能描述
简要描述想要的功能

### 使用场景
为什么需要这个功能

### 实现建议
如何实现（可选）
```

## 发布流程

### 版本发布

1. 更新 `CHANGELOG.md`
2. 更新版本号
3. 创建 Release
4. 构建和发布 Docker 镜像

### 发布命令

```bash
# 创建新版本
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions 将自动构建和发布
```

## 联系方式

- **GitHub Issues**: https://github.com/YOUR_USERNAME/EMS_SYS/issues
- **讨论区**: https://github.com/YOUR_USERNAME/EMS_SYS/discussions

---

感谢您的贡献！
