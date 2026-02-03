# Complete Deployment Guide - Supermarket App

## Project Structure

```
supermarket-app/
├── docker-compose.yml              # Docker Compose for local development
├── docker-compose-k8s.yml          # Docker Compose for K8s bootstrap
├── services/
│   ├── auth-service/               # Authentication & RBAC service
│   ├── bff/                        # Backend for Frontend service
│   ├── core-service/               # Core business logic
│   ├── customer-mgmt/              # Customer management service
│   └── ui-service/                 # Frontend UI service
├── k8s/                            # Kubernetes manifests
│   ├── base/
│   │   ├── namespace-configmap.yaml
│   │   ├── deployments.yaml
│   │   └── services.yaml
│   ├── monitoring/
│   │   └── kubernetes-monitoring.yaml
│   ├── argocd/
│   │   └── application.yaml
│   └── dashboard/
├── terraform/                      # Terraform infrastructure as code
│   ├── main.tf
│   └── variables.tf
└── grafana/                        # Grafana dashboards
    ├── datasources/
    ├── dashboards/
    └── supermarket-dashboard.json
```

## Deployment Options

### Option 1: Docker Compose (Development)

#### Prerequisites
- Docker
- Docker Compose

#### Steps

```bash
# Navigate to project directory
cd supermarket-app

# Start all services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f

# Access services
# - UI: http://localhost:5002
# - BFF API: http://localhost:5000
# - Auth: http://localhost:5003
# - Customer Mgmt: http://localhost:5004
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
# - AlertManager: http://localhost:9093

# Stop services
docker-compose down
```

### Option 2: Kubernetes with Minikube (Recommended for Local K8s)

#### Prerequisites
- Docker
- Minikube
- kubectl
- Helm (optional, for package management)

#### Steps

```bash
# 1. Start Minikube cluster
minikube start --cpus 4 --memory 8192 --disk-size 50000mb

# 2. Build and load Docker images into Minikube
eval $(minikube docker-env)
docker-compose build

# 3. Deploy application
cd k8s
kubectl apply -f base/namespace-configmap.yaml
kubectl apply -f base/deployments.yaml
kubectl apply -f base/services.yaml
kubectl apply -f monitoring/kubernetes-monitoring.yaml

# 4. Install ArgoCD (optional)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 5. Access services
# Get LoadBalancer IPs
kubectl get svc -n supermarket

# Port forward for services
kubectl port-forward -n supermarket svc/ui-service 5002:5002
kubectl port-forward -n supermarket svc/prometheus 9090:9090
kubectl port-forward -n supermarket svc/grafana 3000:3000

# 6. View logs
kubectl logs -f -n supermarket deployment/auth-service
kubectl logs -f -n supermarket deployment/bff-service

# 7. Scale deployments
kubectl scale deployment auth-service -n supermarket --replicas=3

# 8. Stop cluster
minikube stop

# 9. Delete cluster
minikube delete
```

### Option 3: Kubernetes with Kind (Alternative)

#### Prerequisites
- Docker
- Kind
- kubectl

#### Steps

```bash
# 1. Create Kind cluster
kind create cluster --name supermarket

# 2. Load Docker images
docker build -t supermarket-app-auth-service:latest ./services/auth-service
docker build -t supermarket-app-bff-service:latest ./services/bff
kind load docker-image supermarket-app-auth-service:latest --name supermarket
kind load docker-image supermarket-app-bff-service:latest --name supermarket

# 3-8. Same as Minikube steps above

# Delete cluster
kind delete cluster --name supermarket
```

### Option 4: Infrastructure as Code with Terraform

#### Prerequisites
- Terraform >= 1.0
- kubectl
- Kubernetes cluster running (Minikube/Kind)

#### Steps

```bash
# 1. Initialize Terraform
cd terraform
terraform init

# 2. Review plan
terraform plan

# 3. Apply configuration
terraform apply

# 4. Output values
terraform output

# 5. Destroy (cleanup)
terraform destroy
```

## Authentication & RBAC

### Default Users

```
Admin:
  Email: admin@supermarket.com
  Password: admin123

Customer:
  Email: customer@supermarket.com
  Password: customer123
```

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify token
- `GET /api/auth/permissions` - Get user permissions
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout

#### User Management (Admin Only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `PUT /api/users/<user_id>` - Update user
- `DELETE /api/users/<user_id>` - Delete user
- `GET /api/roles` - List all roles

#### Customer Management
- `GET /api/customers/me` - Get current customer profile
- `PUT /api/customers/me` - Update customer profile
- `GET /api/customers/<customer_id>` - Get customer profile
- `GET /api/customers` - List all customers (admin only)
- `GET /api/customers/me/orders` - Get customer orders
- `GET /api/customers/me/loyalty` - Get loyalty info

### RBAC Roles

#### Admin
- Access all tabs: Home, Products, Cart, Orders, Inventory, Admin, Monitoring
- Full API access
- User management
- Role management

#### Customer
- Access tabs: Home, Products, Cart, Orders
- Limited API access (products, orders, profile)
- No user/role management

## Monitoring & Observability

### Prometheus
- Collects metrics from all services
- Retention: 30 days
- Scrape interval: 15 seconds
- URL: http://localhost:9090 (Docker) or kubectl port-forward

### Grafana
- Dashboards for system monitoring
- Default login: admin/admin
- Pre-configured Prometheus datasource
- URL: http://localhost:3000 (Docker) or kubectl port-forward

### AlertManager
- Handles alerts from Prometheus
- Default: http://localhost:9093

### Kubernetes Dashboard
- Built-in K8s web UI
- URL: https://localhost:8443 (Kind) or minikube dashboard

## ArgoCD (GitOps)

### Installation

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access ArgoCD
kubectl port-forward -n argocd svc/argocd-server 8080:443

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Deploy Application with ArgoCD

```bash
kubectl apply -f k8s/argocd/application.yaml

# Monitor sync status
argocd app get supermarket-app
argocd app wait supermarket-app
```

## Services Architecture

### Auth Service (Port 5003)
- JWT token generation
- User authentication
- RBAC enforcement
- User management

### BFF Service (Port 5000)
- API Gateway
- Request routing
- Auth token validation
- Service orchestration

### Customer Management Service (Port 5004)
- Customer profiles
- Loyalty programs
- Order history
- Preferences

### Core Service (Port 5001)
- Product management
- Inventory
- Order processing
- Business logic

### UI Service (Port 5002)
- Frontend application
- Real-time monitoring
- Role-based UI rendering

## Performance & Scalability

### Horizontal Scaling
```bash
# Scale services in Kubernetes
kubectl scale deployment auth-service -n supermarket --replicas=5
kubectl scale deployment bff-service -n supermarket --replicas=3
```

### Resource Limits
- Auth Service: 512Mi RAM, 500m CPU
- BFF Service: 512Mi RAM, 500m CPU
- Core Service: 512Mi RAM, 500m CPU
- Customer Mgmt: 512Mi RAM, 500m CPU
- UI Service: 512Mi RAM, 500m CPU

## Troubleshooting

### Services not communicating
```bash
# Check DNS
kubectl exec -it pod/bff-service -n supermarket -- nslookup auth-service

# Check network policies
kubectl get networkpolicies -n supermarket

# Check service discovery
kubectl get endpoints -n supermarket
```

### High memory usage
```bash
# Check resource usage
kubectl top nodes
kubectl top pod -n supermarket
```

### Logs inspection
```bash
# View service logs
kubectl logs -f -n supermarket deployment/auth-service
kubectl logs --tail=100 -n supermarket pod/auth-service-xyz

# Describe pod for events
kubectl describe pod -n supermarket auth-service-xyz
```

## Production Recommendations

1. **Use managed Kubernetes** (EKS, GKE, AKS) instead of local Minikube
2. **Enable HTTPS/TLS** for all services
3. **Use ConfigMaps and Secrets** for sensitive data
4. **Implement network policies** for service communication
5. **Set up ingress** for external access
6. **Configure persistent volumes** for data
7. **Enable resource quotas** per namespace
8. **Use ReadinessProbes and LivenessProbes**
9. **Configure HPA** (Horizontal Pod Autoscaler)
10. **Implement proper logging** (ELK, Loki, Stackdriver)
11. **Enable monitoring and alerting** (Prometheus, Grafana)
12. **Use GitOps** (ArgoCD) for continuous deployment

## Quick Commands Reference

```bash
# General K8s
kubectl get nodes
kubectl get pods -n supermarket
kubectl get svc -n supermarket
kubectl describe pod <pod-name> -n supermarket
kubectl logs <pod-name> -n supermarket
kubectl exec -it <pod-name> -n supermarket -- /bin/sh

# Scale
kubectl scale deployment <name> -n supermarket --replicas=3

# Port Forward
kubectl port-forward svc/<service> <local-port>:<remote-port> -n supermarket

# Get resource usage
kubectl top nodes
kubectl top pods -n supermarket

# Delete resources
kubectl delete pod <pod-name> -n supermarket
kubectl delete deployment <deployment> -n supermarket
```

---

For more information, see specific service READMEs in each service directory.
