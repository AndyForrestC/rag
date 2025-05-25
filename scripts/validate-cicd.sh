#!/bin/bash

# CI/CD Pipeline Validation Script
# 验证CI/CD流水线的本地环境和配置

set -e

echo "🔍 CI/CD Pipeline Validation Starting..."
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 not found${NC}"
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1 directory exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 directory not found${NC}"
        return 1
    fi
}

# 1. 检查基础工具
echo -e "${BLUE}1. Checking basic tools...${NC}"
TOOLS_OK=true

check_command "git" || TOOLS_OK=false
check_command "curl" || TOOLS_OK=false
check_command "python3" || TOOLS_OK=false
check_command "node" || TOOLS_OK=false
check_command "npm" || TOOLS_OK=false

if ! check_command "docker"; then
    echo -e "${YELLOW}💡 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${YELLOW}⚠️  Please logout and login again to use Docker without sudo${NC}"
    TOOLS_OK=false
fi

if ! check_command "docker-compose"; then
    echo -e "${YELLOW}💡 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 2. 检查项目结构
echo -e "\n${BLUE}2. Checking project structure...${NC}"
PROJECT_OK=true

# 检查关键目录
check_directory ".github/workflows" || PROJECT_OK=false
check_directory "ingestion-service" || PROJECT_OK=false
check_directory "inference-service/backend" || PROJECT_OK=false
check_directory "inference-service/frontend" || PROJECT_OK=false
check_directory "k8s" || PROJECT_OK=false
check_directory "monitoring" || PROJECT_OK=false
check_directory "scripts" || PROJECT_OK=false
check_directory "tests" || PROJECT_OK=false

# 检查关键文件
check_file ".github/workflows/ci.yml" || PROJECT_OK=false
check_file ".github/workflows/cd.yml" || PROJECT_OK=false
check_file ".github/workflows/security.yml" || PROJECT_OK=false
check_file ".github/workflows/performance.yml" || PROJECT_OK=false
check_file "docker-compose.yml" || PROJECT_OK=false
check_file "docker-compose.production.yml" || PROJECT_OK=false
check_file "docker-compose.test.yml" || PROJECT_OK=false
check_file ".env.template" || PROJECT_OK=false

# 3. 检查Docker文件
echo -e "\n${BLUE}3. Checking Dockerfile configurations...${NC}"
DOCKER_OK=true

check_file "ingestion-service/Dockerfile" || DOCKER_OK=false
check_file "inference-service/backend/Dockerfile" || DOCKER_OK=false
check_file "inference-service/frontend/Dockerfile" || DOCKER_OK=false

# 4. 检查依赖文件
echo -e "\n${BLUE}4. Checking dependency files...${NC}"
DEPS_OK=true

check_file "ingestion-service/pyproject.toml" || DEPS_OK=false
check_file "inference-service/backend/pyproject.toml" || DEPS_OK=false
check_file "inference-service/frontend/package.json" || DEPS_OK=false

# 5. 验证GitHub Actions语法
echo -e "\n${BLUE}5. Validating GitHub Actions syntax...${NC}"
ACTIONS_OK=true

for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo -n "Checking $(basename $workflow)... "
        # 使用action-validator或yamllint验证语法
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            echo -e "${GREEN}✅ Valid${NC}"
        else
            echo -e "${RED}❌ Invalid YAML${NC}"
            ACTIONS_OK=false
        fi
    fi
done

# 6. 检查环境变量模板
echo -e "\n${BLUE}6. Checking environment configuration...${NC}"
ENV_OK=true

if [ -f ".env.template" ]; then
    echo -e "${GREEN}✅ .env.template found${NC}"
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
        cp .env.template .env
        echo -e "${YELLOW}📝 Please edit .env file with your actual values${NC}"
    fi
else
    echo -e "${RED}❌ .env.template not found${NC}"
    ENV_OK=false
fi

# 7. 测试Docker构建
echo -e "\n${BLUE}7. Testing Docker builds (this may take a while)...${NC}"
BUILD_OK=true

if command -v docker &> /dev/null; then
    # 检查是否需要sudo权限
    if docker info > /dev/null 2>&1; then
        DOCKER_CMD="docker"
    else
        DOCKER_CMD="sudo docker"
        echo -e "${YELLOW}ℹ️  Using sudo for Docker commands${NC}"
    fi
    
    echo "Testing ingestion-service build..."
    if $DOCKER_CMD build -t test-ingestion-service ./ingestion-service > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ingestion service builds successfully${NC}"
        $DOCKER_CMD rmi test-ingestion-service > /dev/null 2>&1
    else
        echo -e "${RED}❌ Ingestion service build failed${NC}"
        BUILD_OK=false
    fi

    echo "Testing inference-backend build..."
    if $DOCKER_CMD build -t test-inference-backend ./inference-service/backend > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Inference backend builds successfully${NC}"
        $DOCKER_CMD rmi test-inference-backend > /dev/null 2>&1
    else
        echo -e "${RED}❌ Inference backend build failed${NC}"
        BUILD_OK=false
    fi

    echo "Testing inference-frontend build..."
    if $DOCKER_CMD build -t test-inference-frontend ./inference-service/frontend > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Inference frontend builds successfully${NC}"
        $DOCKER_CMD rmi test-inference-frontend > /dev/null 2>&1
    else
        echo -e "${RED}❌ Inference frontend build failed${NC}"
        BUILD_OK=false
    fi
else
    echo -e "${YELLOW}⚠️  Docker not available, skipping build tests${NC}"
    BUILD_OK=false
fi

# 8. 检查测试配置
echo -e "\n${BLUE}8. Checking test configurations...${NC}"
TEST_OK=true

# 检查Python测试
if [ -f "ingestion-service/pyproject.toml" ]; then
    if grep -q "pytest" ingestion-service/pyproject.toml; then
        echo -e "${GREEN}✅ Ingestion service has pytest configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Pytest not found in ingestion-service pyproject.toml${NC}"
        TEST_OK=false
    fi
fi

if [ -f "inference-service/backend/pyproject.toml" ]; then
    if grep -q "pytest" inference-service/backend/pyproject.toml; then
        echo -e "${GREEN}✅ Inference backend has pytest configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Pytest not found in inference-backend pyproject.toml${NC}"
        TEST_OK=false
    fi
fi

# 检查前端测试
if [ -f "inference-service/frontend/package.json" ]; then
    if grep -q "jest" inference-service/frontend/package.json; then
        echo -e "${GREEN}✅ Frontend has Jest configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Jest not found in frontend package.json${NC}"
        TEST_OK=false
    fi
fi

# 9. 创建GitHub Secrets检查清单
echo -e "\n${BLUE}9. GitHub Secrets Checklist...${NC}"
cat << EOF
${YELLOW}📋 Required GitHub Secrets (set these in your repository settings):${NC}

${GREEN}Required for CI/CD:${NC}
- DOCKER_USERNAME (your Docker Hub username)
- DOCKER_PASSWORD (your Docker Hub password)
- SONAR_TOKEN (your SonarCloud token)

${GREEN}Optional for enhanced features:${NC}
- KUBECONFIG_STAGING (base64 encoded kubeconfig for staging)
- KUBECONFIG_PRODUCTION (base64 encoded kubeconfig for production)
- SLACK_WEBHOOK_URL (Slack webhook for notifications)
- CODECOV_TOKEN (Codecov integration)

${BLUE}To set these:${NC}
1. Go to your GitHub repository
2. Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret with its value
EOF

# 10. 总结报告
echo -e "\n${BLUE}=========================================="
echo -e "📊 VALIDATION SUMMARY"
echo -e "==========================================${NC}"

if [ "$TOOLS_OK" = true ]; then
    echo -e "${GREEN}✅ Basic tools: PASSED${NC}"
else
    echo -e "${RED}❌ Basic tools: FAILED${NC}"
fi

if [ "$PROJECT_OK" = true ]; then
    echo -e "${GREEN}✅ Project structure: PASSED${NC}"
else
    echo -e "${RED}❌ Project structure: FAILED${NC}"
fi

if [ "$DOCKER_OK" = true ]; then
    echo -e "${GREEN}✅ Docker configuration: PASSED${NC}"
else
    echo -e "${RED}❌ Docker configuration: FAILED${NC}"
fi

if [ "$DEPS_OK" = true ]; then
    echo -e "${GREEN}✅ Dependencies: PASSED${NC}"
else
    echo -e "${RED}❌ Dependencies: FAILED${NC}"
fi

if [ "$ACTIONS_OK" = true ]; then
    echo -e "${GREEN}✅ GitHub Actions syntax: PASSED${NC}"
else
    echo -e "${RED}❌ GitHub Actions syntax: FAILED${NC}"
fi

if [ "$ENV_OK" = true ]; then
    echo -e "${GREEN}✅ Environment configuration: PASSED${NC}"
else
    echo -e "${RED}❌ Environment configuration: FAILED${NC}"
fi

if [ "$BUILD_OK" = true ]; then
    echo -e "${GREEN}✅ Docker builds: PASSED${NC}"
else
    echo -e "${RED}❌ Docker builds: FAILED${NC}"
fi

if [ "$TEST_OK" = true ]; then
    echo -e "${GREEN}✅ Test configuration: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Test configuration: NEEDS ATTENTION${NC}"
fi

# 最终状态
if [ "$TOOLS_OK" = true ] && [ "$PROJECT_OK" = true ] && [ "$DOCKER_OK" = true ] && [ "$DEPS_OK" = true ] && [ "$ACTIONS_OK" = true ] && [ "$ENV_OK" = true ]; then
    echo -e "\n${GREEN}🎉 CI/CD Pipeline is ready!${NC}"
    echo -e "${GREEN}You can now:${NC}"
    echo -e "${GREEN}1. Push your code to GitHub${NC}"
    echo -e "${GREEN}2. Create a pull request to trigger CI${NC}"
    echo -e "${GREEN}3. Merge to main to trigger CD${NC}"
else
    echo -e "\n${YELLOW}⚠️  CI/CD Pipeline needs attention${NC}"
    echo -e "${YELLOW}Please fix the issues above before proceeding${NC}"
fi

echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Edit .env file with your actual configuration"
echo "2. Set up GitHub repository secrets"
echo "3. Push code to GitHub repository"
echo "4. Check GitHub Actions tab for workflow execution"

echo -e "\n${BLUE}For detailed troubleshooting, see: CI-CD-GUIDE.md${NC}"
