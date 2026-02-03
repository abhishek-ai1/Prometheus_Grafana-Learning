#!/bin/bash

# Supermarket App Deployment Script
# Supports multiple deployment options: Docker Compose, Minikube, Kind, Terraform

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 is installed"
}

# Main menu
show_menu() {
    print_header "Supermarket App - Deployment Options"
    echo "1. Docker Compose (Local Development)"
    echo "2. Kubernetes with Minikube"
    echo "3. Kubernetes with Kind"
    echo "4. Terraform (Infrastructure as Code)"
    echo "5. ArgoCD (GitOps Deployment)"
    echo "6. Clean Up & Stop Services"
    echo "7. View Service Status"
    echo "0. Exit"
    echo ""
}

# Docker Compose Deployment
deploy_docker_compose() {
    print_header "Starting Docker Compose Deployment"
    
    check_command docker || return 1
    check_command docker-compose || return 1
    
    print_warning "Building Docker images..."
    docker-compose build
    
    print_warning "Starting services..."
    docker-compose up -d
    
    sleep 5
    
    print_header "Docker Compose Services"
    docker-compose ps
    
    print_success "Docker Compose deployment complete!"
    echo ""
    echo "Access services at:"
    echo "  • UI: http://localhost:5002"
    echo "  • BFF API: http://localhost:5000"
    echo "  • Auth: http://localhost:5003"
    echo "  • Customer Mgmt: http://localhost:5004"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3000 (admin/admin)"
    echo ""
}

# Minikube Deployment
deploy_minikube() {
    print_header "Starting Minikube Deployment"
    
    check_command minikube || return 1
    check_command kubectl || return 1
    
    print_warning "Starting Minikube cluster..."
    minikube start --cpus 4 --memory 8192 --disk-size 50000mb
    
    print_warning "Setting up Docker environment..."
    eval $(minikube docker-env)
    
    print_warning "Building Docker images..."
    docker-compose build
    
    print_warning "Deploying to Kubernetes..."
    kubectl apply -f k8s/base/namespace-configmap.yaml
    kubectl apply -f k8s/base/deployments.yaml
    kubectl apply -f k8s/base/services.yaml
    kubectl apply -f k8s/monitoring/kubernetes-monitoring.yaml
    
    sleep 10
    
    print_header "Minikube Services"
    kubectl get svc -n supermarket
    
    print_success "Minikube deployment complete!"
    echo ""
    echo "To access services, use port-forward:"
    echo "  • kubectl port-forward -n supermarket svc/ui-service 5002:5002"
    echo "  • kubectl port-forward -n supermarket svc/prometheus 9090:9090"
    echo "  • kubectl port-forward -n supermarket svc/grafana 3000:3000"
    echo ""
}

# Kind Deployment
deploy_kind() {
    print_header "Starting Kind Deployment"
    
    check_command kind || return 1
    check_command kubectl || return 1
    
    print_warning "Creating Kind cluster..."
    kind create cluster --name supermarket || print_warning "Cluster might already exist"
    
    print_warning "Building Docker images..."
    docker-compose build
    
    print_warning "Loading images into Kind..."
    docker save supermarket-app-auth-service:latest | kind load image-archive - --name supermarket
    docker save supermarket-app-bff-service:latest | kind load image-archive - --name supermarket
    docker save supermarket-app-core-service:latest | kind load image-archive - --name supermarket
    docker save supermarket-app-customer-mgmt:latest | kind load image-archive - --name supermarket
    docker save supermarket-app-ui-service:latest | kind load image-archive - --name supermarket
    
    print_warning "Deploying to Kubernetes..."
    kubectl apply -f k8s/base/namespace-configmap.yaml
    kubectl apply -f k8s/base/deployments.yaml
    kubectl apply -f k8s/base/services.yaml
    kubectl apply -f k8s/monitoring/kubernetes-monitoring.yaml
    
    sleep 10
    
    print_header "Kind Services"
    kubectl get svc -n supermarket
    
    print_success "Kind deployment complete!"
    echo ""
    echo "To access services, use port-forward:"
    echo "  • kubectl port-forward -n supermarket svc/ui-service 5002:5002"
    echo "  • kubectl port-forward -n supermarket svc/prometheus 9090:9090"
    echo "  • kubectl port-forward -n supermarket svc/grafana 3000:3000"
    echo ""
}

# Terraform Deployment
deploy_terraform() {
    print_header "Starting Terraform Deployment"
    
    check_command terraform || return 1
    check_command kubectl || return 1
    
    print_warning "Initializing Terraform..."
    cd terraform
    terraform init
    
    print_warning "Planning infrastructure..."
    terraform plan
    
    echo ""
    read -p "Do you want to apply this configuration? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_warning "Terraform deployment cancelled"
        cd ..
        return 1
    fi
    
    print_warning "Applying configuration..."
    terraform apply -auto-approve
    
    print_header "Terraform Outputs"
    terraform output
    
    cd ..
    
    print_success "Terraform deployment complete!"
    echo ""
}

# ArgoCD Deployment
deploy_argocd() {
    print_header "Installing ArgoCD"
    
    check_command kubectl || return 1
    
    print_warning "Creating ArgoCD namespace..."
    kubectl create namespace argocd || print_warning "Namespace might already exist"
    
    print_warning "Installing ArgoCD..."
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    print_warning "Waiting for ArgoCD to be ready..."
    sleep 15
    
    print_warning "Deploying application..."
    kubectl apply -f k8s/argocd/application.yaml
    
    print_header "ArgoCD Status"
    kubectl get pods -n argocd
    
    print_success "ArgoCD deployment complete!"
    echo ""
    echo "To access ArgoCD:"
    echo "  • kubectl port-forward -n argocd svc/argocd-server 8080:443"
    echo "  • Get password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d"
    echo ""
}

# Cleanup
cleanup() {
    print_header "Cleanup Options"
    echo "1. Stop and remove Docker Compose services"
    echo "2. Delete Minikube cluster"
    echo "3. Delete Kind cluster"
    echo "4. Delete ArgoCD"
    echo "5. Cancel"
    echo ""
    read -p "Select option (1-5): " cleanup_option
    
    case $cleanup_option in
        1)
            print_warning "Stopping Docker Compose services..."
            docker-compose down -v
            print_success "Docker Compose services stopped"
            ;;
        2)
            print_warning "Deleting Minikube cluster..."
            minikube delete
            print_success "Minikube cluster deleted"
            ;;
        3)
            print_warning "Deleting Kind cluster..."
            kind delete cluster --name supermarket
            print_success "Kind cluster deleted"
            ;;
        4)
            print_warning "Deleting ArgoCD..."
            kubectl delete namespace argocd
            print_success "ArgoCD deleted"
            ;;
        5)
            print_warning "Cleanup cancelled"
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

# View Status
view_status() {
    print_header "Service Status"
    
    echo "Docker Compose Services:"
    docker-compose ps 2>/dev/null || print_warning "Docker Compose not running"
    
    echo ""
    echo "Kubernetes Services:"
    kubectl get svc -n supermarket 2>/dev/null || print_warning "Kubernetes not running"
    
    echo ""
    echo "Pod Status:"
    kubectl get pods -n supermarket 2>/dev/null || print_warning "Kubernetes not running"
}

# Main Loop
main() {
    while true; do
        show_menu
        read -p "Select option (0-7): " option
        
        case $option in
            1)
                deploy_docker_compose
                ;;
            2)
                deploy_minikube
                ;;
            3)
                deploy_kind
                ;;
            4)
                deploy_terraform
                ;;
            5)
                deploy_argocd
                ;;
            6)
                cleanup
                ;;
            7)
                view_status
                ;;
            0)
                print_success "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option"
                ;;
        esac
    done
}

# Run main
main
