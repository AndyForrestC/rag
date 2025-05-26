# 使用官方Node.js基础镜像
FROM node:18-alpine AS base

# 设置工作目录
WORKDIR /app

# 安装依赖阶段 - 包含开发依赖用于构建
FROM base AS deps
RUN apk add --no-cache libc6-compat

# 复制package文件
COPY package*.json ./
# 安装所有依赖（包括开发依赖）用于构建
RUN npm ci

# 生产依赖阶段 - 仅生产依赖
FROM base AS production-deps
RUN apk add --no-cache libc6-compat

COPY package*.json ./
RUN npm ci --only=production

# 构建阶段
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 设置环境变量
ENV NEXT_TELEMETRY_DISABLED 1

# 构建应用
RUN npm run build

# 生产运行阶段
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 创建nextjs用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=builder /app/public ./public

# 自动利用输出跟踪来减少镜像大小
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# 暴露端口
EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# 启动命令
CMD ["node", "server.js"]
