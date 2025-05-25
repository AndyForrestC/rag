#!/bin/bash

# RAG Microservices Quick Start Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  RAG Microservices Platform${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed!"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [[ ! -f .env ]]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.template .env
        print_status "Please edit .env file with your configuration before continuing."
        echo "Press Enter to continue after editing .env file..."
        read
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data/uploads
    mkdir -p data/vector_store
    
    print_status "Environment setup completed!"
}

# Function to start services
start_services() {
    print_status "Starting RAG microservices..."
    
    # Pull latest images if they exist
    docker-compose pull || true
    
    # Start services
    docker-compose up -d
    
    print_status "Services are starting up..."
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Function to check service health
check_service_health() {
    print_status "Checking service health..."
    
    services=("milvus:19530" "ingestion-service:8000" "inference-backend:8000" "inference-frontend:3000")
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1 || curl -f -s "http://localhost:$port" >/dev/null 2>&1; then
            print_status "$name is healthy ✓"
        else
            print_warning "$name might still be starting up..."
        fi
    done
}

# Function to show service URLs
show_urls() {
    echo
    print_header
    echo -e "${GREEN}🚀 RAG Microservices are running!${NC}"
    echo
    echo -e "${YELLOW}Service URLs:${NC}"
    echo -e "  Frontend:        ${BLUE}http://localhost:3000${NC}"
    echo -e "  Ingestion API:   ${BLUE}http://localhost:8001${NC}"
    echo -e "  Inference API:   ${BLUE}http://localhost:8002${NC}"
    echo -e "  Milvus Admin:    ${BLUE}http://localhost:9001${NC}"
    echo
    echo -e "${YELLOW}Monitoring (if enabled):${NC}"
    echo -e "  Grafana:         ${BLUE}http://localhost:3001${NC} (admin/admin)"
    echo -e "  Prometheus:      ${BLUE}http://localhost:9090${NC}"
    echo
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo -e "  View logs:       ${BLUE}docker-compose logs -f [service-name]${NC}"
    echo -e "  Stop services:   ${BLUE}docker-compose down${NC}"
    echo -e "  Restart:         ${BLUE}docker-compose restart [service-name]${NC}"
    echo
}

# Function to show help
show_help() {
    echo "RAG Microservices Quick Start Script"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  start         Start all services (default)"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  logs          Show logs for all services"
    echo "  status        Show status of all services"
    echo "  monitoring    Start monitoring stack (Prometheus + Grafana)"
    echo "  clean         Clean up all containers and volumes"
    echo "  help          Show this help message"
}

# Function to stop services
stop_services() {
    print_status "Stopping RAG microservices..."
    docker-compose down
    print_status "Services stopped!"
}

# Function to restart services
restart_services() {
    print_status "Restarting RAG microservices..."
    docker-compose restart
    print_status "Services restarted!"
}

# Function to show logs
show_logs() {
    print_status "Showing logs for all services..."
    docker-compose logs -f
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
}

# Function to start monitoring
start_monitoring() {
    print_status "Starting monitoring stack..."
    docker-compose -f docker-compose.monitoring.yml up -d
    print_status "Monitoring stack started!"
    echo -e "Grafana: ${BLUE}http://localhost:3001${NC} (admin/admin)"
    echo -e "Prometheus: ${BLUE}http://localhost:9090${NC}"
}

# Function to clean up
clean_up() {
    print_warning "This will remove all containers, networks, and volumes!"
    echo "Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker-compose -f docker-compose.monitoring.yml down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Main function
main() {
    case "${1:-start}" in
        start)
            print_header
            check_prerequisites
            setup_environment
            start_services
            show_urls
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        monitoring)
            start_monitoring
            ;;
        clean)
            clean_up
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
