# 多阶段构建 - 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json* ./
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}

RUN npm run build

# 生产阶段
FROM node:20-alpine AS production

WORKDIR /app

# 复制构建产物
COPY --from=builder /app/.output /app/.output

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/_health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# 启动应用
ENTRYPOINT ["node", ".output/server/index.mjs"]
