# RAG Microservices CI/CD Guide

本文档描述了RAG微服务项目的完整CI/CD流程设置和使用方法。

## 🏗️ 架构概览

该项目包含以下组件：
- **Ingestion Service**: 文档摄取和向量化服务 (Python/FastAPI)
- **Inference Service Backend**: RAG推理后端服务 (Python/FastAPI + NeMo Guardrails)
- **Inference Service Frontend**: Web界面 (Next.js/React)
- **Milvus**: GPU加速向量数据库
- **Nginx**: 负载均衡和反向代理

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd rag

# 复制环境变量模板
cp .env.template .env

# 编辑环境变量
vim .env
```

### 2. 本地开发

```bash
# 启动开发环境
./scripts/deploy.sh

# 或者手动启动
docker-compose up -d
```

### 3. 生产部署

```bash
# 构建并部署到生产环境
./scripts/deploy.sh -e production -b

# 或者部署到Kubernetes
./scripts/deploy.sh -e production -b -k
```

## 🔄 CI/CD 流程

### GitHub Actions 工作流

我们使用独立的 GitHub Actions 工作流实现 CI/CD 流水线：

#### 1. **持续集成 (CI)** - `.github/workflows/ci.yml`
- **测试阶段** (并行执行):
  - **Python服务测试**: 
    - 代码质量检查 (Black, Flake8, MyPy)
    - 单元测试 (Pytest)
    - 安全扫描 (Safety)
    - 测试覆盖率报告
  - **前端测试**:
    - ESLint代码检查
    - TypeScript类型检查
    - Jest单元测试
    - 构建验证
- **代码质量分析**: SonarCloud静态代码分析
- **集成测试**: 端到端系统测试
- **Docker构建测试**: 镜像构建验证

#### 2. **持续部署 (CD)** - `.github/workflows/cd.yml`
- **构建和推送阶段**:
  - Docker镜像构建和推送
  - 多平台支持 (AMD64/ARM64)
  - 镜像缓存优化
- **部署阶段**:
  - **Staging环境**: 自动部署（CI成功后）
  - **Production环境**: 手动审批部署
  - 健康检查和烟雾测试
  - 自动回滚功能

#### 3. **安全扫描** - `.github/workflows/security.yml`
- Trivy漏洞扫描
- Semgrep代码安全分析
- OWASP依赖检查
- 定时安全扫描

#### 4. **性能测试** - `.github/workflows/performance.yml`
- k6负载测试
- 性能回归检测
- 自动化性能报告

### 触发条件

#### CI 流水线触发：
- **Push到main/develop分支**: 运行完整CI流程
- **Pull Request**: 运行CI测试和质量检查
- **定时触发**: 每日自动安全扫描

#### CD 流水线触发：
- **CI成功完成**: 自动触发部署到staging
- **手动触发**: 可选择部署环境（staging/production）
- **强制部署**: 可绕过CI检查（紧急情况）

### 工作流依赖关系

```
CI (ci.yml) → CD (cd.yml)
     ↓
Security (security.yml)
     ↓
Performance (performance.yml)
```

## 🛠️ 配置说明

### GitHub Secrets

在GitHub仓库设置中添加以下Secrets：

```
DOCKER_USERNAME=你的Docker Hub用户名
DOCKER_PASSWORD=你的Docker Hub密码
SONAR_TOKEN=你的SonarCloud token
```

### 环境变量

参考 `.env.template` 文件配置以下环境变量：

- **Docker Registry**: Docker Hub凭据
- **数据库配置**: Milvus、Redis等
- **API Keys**: OpenAI、Cohere等
- **域名配置**: 生产环境域名

## 📊 监控和日志

### Prometheus + Grafana

启动监控组件：

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

访问地址：
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093

### 应用指标

每个微服务都暴露以下指标：
- 请求数量和延迟
- 错误率
- 系统资源使用
- 自定义业务指标

## 🔒 安全最佳实践

### 1. 容器安全
- 使用非root用户运行容器
- 最小化镜像大小
- 定期更新基础镜像

### 2. 网络安全
- Nginx速率限制
- HTTPS/TLS加密
- 网络隔离

### 3. 数据安全
- 敏感数据加密
- 访问控制
- 审计日志

## 🚀 部署选项

### 1. Docker Compose (推荐用于开发和小规模部署)

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.production.yml up -d
```

### 2. Kubernetes (推荐用于生产环境)

```bash
# 应用所有K8s配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get pods -n rag-system
```

### 3. 云平台部署

支持部署到：
- AWS EKS/ECS
- Google GKE
- Azure AKS
- Digital Ocean Kubernetes

## 🧪 测试策略

### 单元测试
```bash
# Python服务
cd ingestion-service
poetry run pytest tests/ -v --cov

# 前端
cd inference-service/frontend
npm test -- --coverage
```

### 集成测试
```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
pytest tests/integration/
```

### 性能测试
```bash
# 使用k6进行负载测试
docker run --rm -v $(pwd)/tests/performance:/scripts grafana/k6 run /scripts/chat-load-test.js

# 生成性能报告
node scripts/generate-performance-report.js
```

### 端到端测试
```bash
# Playwright E2E测试（前端）
cd inference-service/frontend
npm run test:e2e
```

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 检查容器日志
docker-compose logs [service-name]

# 检查容器状态
docker-compose ps
```

#### 2. 数据库连接问题
```bash
# 检查Milvus健康状态
curl http://localhost:19121/health

# 重启数据库服务
docker-compose restart milvus
```

#### 3. 内存不足
```bash
# 监控资源使用
docker stats

# 调整docker-compose中的资源限制
# 在production配置中增加内存分配
```

#### 4. CI/CD流水线失败

**测试阶段失败：**
- 检查依赖项是否正确安装
- 验证测试数据库连接
- 查看详细的pytest输出

**构建阶段失败：**
- 验证Dockerfile语法
- 检查依赖项版本冲突
- 确认基础镜像可用性

**部署阶段失败：**
- 验证Docker Hub凭据
- 检查Kubernetes集群状态
- 确认环境变量配置

### 日志分析

#### 1. 应用日志
```bash
# 实时查看日志
docker-compose logs -f [service-name]

# 查看最近的错误
docker-compose logs [service-name] | grep ERROR
```

#### 2. 性能日志
```bash
# Nginx访问日志
docker-compose exec nginx tail -f /var/log/nginx/access.log

# 应用性能指标
curl http://localhost:8000/metrics
```

### 监控告警

#### 设置告警规则
AlertManager配置在 `monitoring/alertmanager.yml` 中：

```yaml
# 示例告警配置
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
```

## 📈 性能优化

### 1. 应用层优化

#### Python服务
- 使用异步处理 (FastAPI + asyncio)
- 实现连接池
- 启用缓存机制
- 优化数据库查询

#### 前端优化
- 代码分割和懒加载
- 图片优化
- CDN使用
- 缓存策略

### 2. 基础设施优化

#### Docker优化
```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder
# ... 构建阶段

FROM python:3.11-slim as runtime
# ... 运行时镜像
```

#### Nginx优化
```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain application/json;

# 设置缓存头
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 数据库优化

#### Milvus配置
```yaml
# 在docker-compose中优化Milvus
milvus:
  environment:
    - MILVUS_CACHE_SIZE=2GB
    - MILVUS_CPU_CACHE_CAPACITY=4
```

## 🔄 持续改进

### 代码质量指标

跟踪以下指标：
- **测试覆盖率**: >80%
- **代码复杂度**: <10 (McCabe)
- **技术债务比例**: <5%
- **安全漏洞**: 0个高危

### 性能基准

建立性能基准：
- **响应时间**: 95%请求 <200ms
- **吞吐量**: >1000 req/s
- **可用性**: >99.9%
- **错误率**: <0.1%

### DevOps指标

监控DevOps效率：
- **部署频率**: 每天
- **变更前置时间**: <1小时
- **平均恢复时间**: <30分钟
- **变更失败率**: <5%

## 📚 最佳实践总结

### 1. 版本控制
- 使用语义化版本 (Semantic Versioning)
- 保持清晰的提交消息
- 使用分支策略 (GitFlow)

### 2. 测试策略
- 测试金字塔：单元测试 > 集成测试 > E2E测试
- 测试驱动开发 (TDD)
- 自动化回归测试

### 3. 安全实践
- 定期依赖项更新
- 秘密管理 (GitHub Secrets)
- 最小权限原则

### 4. 监控和可观测性
- 结构化日志记录
- 分布式追踪
- 业务指标监控

### 5. 部署策略
- 蓝绿部署
- 金丝雀发布
- 滚动更新

## 🆘 获取帮助

### 文档和资源
- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Kubernetes指南](https://kubernetes.io/docs/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Next.js文档](https://nextjs.org/docs)

### 社区支持
- GitHub Issues
- Stack Overflow
- Discord/Slack社区

---

## 🎯 快速检查清单

部署前确认：

- [ ] 所有测试通过
- [ ] 安全扫描无高危漏洞
- [ ] 性能测试满足要求
- [ ] 监控告警配置正确
- [ ] 备份和恢复策略就绪
- [ ] 文档更新完整
- [ ] 团队培训完成

**恭喜！🎉 你的RAG微服务项目CI/CD流水线已完全配置并可投入生产使用。**

---

*最后更新: $(date)*
*版本: 1.0.0*
