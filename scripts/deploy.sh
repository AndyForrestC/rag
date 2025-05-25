#!/bin/bash

# RAG Microservices Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
BUILD_IMAGES=false
DEPLOY_K8S=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --environment    Environment (development/staging/production) [default: development]"
    echo "  -b, --build          Build Docker images"
    echo "  -k, --kubernetes     Deploy to Kubernetes"
    echo "  -h, --help          Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGES=true
            shift
            ;;
        -k|--kubernetes)
            DEPLOY_K8S=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option $1"
            usage
            ;;
    esac
done

print_status "Starting deployment for environment: $ENVIRONMENT"

# Check if .env file exists
if [[ ! -f .env ]]; then
    print_warning ".env file not found. Please copy .env.template to .env and configure it."
    cp .env.template .env
    print_status "Created .env file from template. Please configure it before proceeding."
    exit 1
fi

# Load environment variables
source .env

# Build Docker images if requested
if [[ "$BUILD_IMAGES" == true ]]; then
    print_status "Building Docker images..."
    
    print_status "Building ingestion-service..."
    docker build -t ${DOCKER_USERNAME}/rag-ingestion-service:latest ./ingestion-service/
    
    print_status "Building inference-backend..."
    docker build -t ${DOCKER_USERNAME}/rag-inference-backend:latest ./inference-service/backend/
    
    print_status "Building inference-frontend..."
    docker build -t ${DOCKER_USERNAME}/rag-inference-frontend:latest ./inference-service/frontend/
    
    print_status "All Docker images built successfully!"
fi

# Deploy based on environment
if [[ "$DEPLOY_K8S" == true ]]; then
    print_status "Deploying to Kubernetes..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/
    
    print_status "Kubernetes deployment completed!"
    
elif [[ "$ENVIRONMENT" == "production" ]]; then
    print_status "Deploying to production with Docker Compose..."
    docker-compose -f docker-compose.production.yml up -d
    
elif [[ "$ENVIRONMENT" == "staging" ]]; then
    print_status "Deploying to staging with Docker Compose..."
    docker-compose -f docker-compose.yml up -d
    
else
    print_status "Starting development environment..."
    docker-compose up -d
fi

print_status "Deployment completed successfully!"

# Show service URLs
print_status "Service URLs:"
if [[ "$DEPLOY_K8S" == true ]]; then
    echo "  Frontend: https://${PRODUCTION_DOMAIN}"
    echo "  API: https://${PRODUCTION_DOMAIN}/api"
else
    echo "  Frontend: http://localhost:3000"
    echo "  Inference API: http://localhost:8002"
    echo "  Ingestion API: http://localhost:8001"
    echo "  Milvus Admin: http://localhost:9001"
fi
