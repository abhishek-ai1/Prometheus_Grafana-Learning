# Supermarket Microservices Application

A production-ready supermarket management system built with microservices architecture, Kubernetes orchestration, and comprehensive monitoring using Prometheus and Grafana.

## Architecture Overview

### Microservices

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Service (5002)                         │
│              Frontend Web Application                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                 BFF Service (5000)                           │
│         Backend for Frontend - API Gateway                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│               Core Service (5001)                            │
│    Business Logic - Products, Orders, Inventory              │
└─────────────────────────────────────────────────────────────┘
```

### Monitoring Stack

```
┌──────────────────────────────────────────────────────────┐
│              Microservices (with metrics)                 │
│        • BFF Service (/metrics on :5000)                 │
│        • Core Service (/metrics on :5001)               │
│        • UI Service (/metrics on :5002)                 │
└──────────────────┬───────────────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
┌───────▼──────┐      ┌───────▼──────┐
│  Prometheus  │      │   Grafana    │
│   (9090)     │      │   (3000)     │
└──────────────┘      └──────────────┘
```

## Project Structure

```
supermarket-app/
├── services/
│   ├── bff/                    # Backend for Frontend
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── core-service/           # Core Business Logic
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── ui-service/             # Frontend UI
│       ├── main.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── static/
│           ├── index.html
│           ├── products.html
│           └── orders.html
├── k8s/
│   ├── services/
│   │   ├── bff.yaml           # BFF Deployment & Service
│   │   ├── core-service.yaml  # Core Service Deployment & Service
│   │   └── ui-service.yaml    # UI Service Deployment & Service
│   ├── monitoring/
│   │   ├── prometheus.yaml    # Prometheus Deployment
│   │   └── grafana.yaml       # Grafana Deployment
│   └── dashboard/
│       └── dashboard-user.yaml # Kubernetes Dashboard Setup
├── docker-compose.yml          # Local development setup
├── build-images.sh            # Build Docker images
├── deploy-k8s.sh              # Deploy to Kubernetes
├── run-local.sh               # Start local stack
└── stop-local.sh              # Stop local stack
```

## Features

### Microservices
- **BFF Service**: API gateway pattern, coordinates between UI and Core services
- **Core Service**: Business logic for products, inventory, and orders
- **UI Service**: Web frontend with product browsing and order management

### Monitoring
- **Prometheus**: Time-series metrics collection from all services
- **Grafana**: Dashboard and visualization platform
- **Built-in Metrics**:
  - Request counts and rates
  - Request latency/duration
  - Orders created counter
  - Products queried counter
  - Service health endpoints

### Kubernetes
- Service discovery and orchestration
- Auto-scaling capabilities (configurable replicas)
- Health checks (liveness & readiness probes)
- Load balancing
- Resource limits and requests
- RBAC for monitoring components

### Kubernetes Dashboard
- Cluster management UI
- Pod and service monitoring
- Resource visualization
- Admin user setup

## Prerequisites

### For Local Development (Docker Compose)
- Docker (version 20.10+)
- Docker Compose (version 1.29+)

### For Kubernetes Deployment
- Kubernetes cluster (v1.19+)
- kubectl CLI tool
- Docker registry access (or local Docker daemon for k3s/minikube)

## Quick Start - Local Development

### 1. Clone and Navigate

```bash
cd supermarket-app
```

### 2. Run Local Stack

```bash
chmod +x run-local.sh
./run-local.sh
```

This will:
- Build all Docker images
- Start all services with Docker Compose
- Initialize Prometheus and Grafana

### 3. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| UI | http://localhost:5002 | - |
| BFF API | http://localhost:5000 | - |
| Core API | http://localhost:5001 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |

### 4. Test the Application

#### Get Products
```bash
curl http://localhost:5000/api/products
```

#### Create Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "name": "Milk", "price": 3.99, "quantity": 2},
      {"id": "4", "name": "Apples", "price": 1.99, "quantity": 3}
    ]
  }'
```

#### Check Service Health
```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

#### View Metrics
```bash
curl http://localhost:5000/metrics  # BFF metrics
curl http://localhost:5001/metrics  # Core Service metrics
curl http://localhost:5002/metrics  # UI Service metrics
```

### 5. Stop Local Stack

```bash
chmod +x stop-local.sh
./stop-local.sh
```

Or use Docker Compose directly:
```bash
docker-compose down
```

## Kubernetes Deployment

### 1. Build and Push Images

For local Kubernetes (minikube/k3s):
```bash
chmod +x build-images.sh
./build-images.sh
```

For remote registry:
```bash
docker build -t your-registry/supermarket/bff:latest ./services/bff
docker build -t your-registry/supermarket/core-service:latest ./services/core-service
docker build -t your-registry/supermarket/ui-service:latest ./services/ui-service
docker push your-registry/supermarket/bff:latest
docker push your-registry/supermarket/core-service:latest
docker push your-registry/supermarket/ui-service:latest
```

Update image references in `k8s/services/*.yaml` files.

### 2. Deploy to Kubernetes

```bash
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

This will:
- Create `monitoring` namespace for Prometheus and Grafana
- Create `supermarket` namespace for application services
- Create `kubernetes-dashboard` namespace for the dashboard
- Deploy all services with proper configurations

### 3. Verify Deployment

```bash
# Check all namespaces
kubectl get ns

# Check supermarket services
kubectl get pods,svc -n supermarket

# Check monitoring stack
kubectl get pods,svc -n monitoring

# Check dashboard
kubectl get svc -n kubernetes-dashboard
```

### 4. Access Services in Kubernetes

#### Port Forward to Prometheus
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Access: http://localhost:9090
```

#### Port Forward to Grafana
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Access: http://localhost:3000 (admin/admin)
```

#### Get Kubernetes Dashboard Token
```bash
kubectl -n kubernetes-dashboard create token admin-user
```

#### Port Forward to Dashboard
```bash
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 8443:443
# Access: https://localhost:8443
```

#### Get LoadBalancer IPs
```bash
kubectl get svc -n supermarket
kubectl get svc -n monitoring
```

## Monitoring & Observability

### Prometheus

Prometheus automatically discovers and scrapes metrics from services via Kubernetes service discovery.

**Scrape Targets:**
- BFF Service: `/metrics` on port 5000
- Core Service: `/metrics` on port 5001
- UI Service: `/metrics` on port 5002
- Kubernetes API Server, Nodes, Pods

**Key Metrics:**

```promql
# BFF Service
bff_requests_total
bff_request_duration_seconds
bff_core_service_calls_total

# Core Service
core_service_requests_total
core_service_request_duration_seconds
orders_created_total
products_queried_total

# UI Service
ui_service_requests_total
ui_service_request_duration_seconds
page_views_total
```

### Grafana

Pre-configured dashboards available:
- **Supermarket System Overview**: High-level metrics across all services
- Can add custom dashboards for specific services

**Default Datasource:** Prometheus (http://prometheus:9090)

**Add Custom Dashboards:**
1. Log in to Grafana (admin/admin)
2. Go to Dashboards → New → Create
3. Select Prometheus as datasource
4. Add panels with desired metrics

## Service APIs

### BFF Service (http://localhost:5000)

```
GET  /health              - Service health status
GET  /metrics             - Prometheus metrics
GET  /api/products        - List all products
GET  /api/products/{id}   - Get product details
POST /api/orders          - Create new order
GET  /api/orders/{id}     - Get order details
```

### Core Service (http://localhost:5001)

```
GET  /health              - Service health status
GET  /metrics             - Prometheus metrics
GET  /products            - List all products
GET  /products/{id}       - Get product details
POST /products            - Create new product
POST /orders              - Create new order
GET  /orders/{id}         - Get order details
PUT  /orders/{id}/status  - Update order status
```

### UI Service (http://localhost:5002)

```
GET  /health              - Service health status
GET  /metrics             - Prometheus metrics
GET  /                    - Home page
GET  /products            - Products page
GET  /orders              - Orders page
GET  /config              - UI configuration
```

## Environment Variables

### BFF Service
- `ENVIRONMENT`: Deployment environment (development/production)

### Core Service
- `ENVIRONMENT`: Deployment environment (development/production)

### UI Service
- `ENVIRONMENT`: Deployment environment (development/production)
- `API_BASE_URL`: Backend API base URL (default: http://bff-service:5000)

### Prometheus
- Configured via ConfigMap in Kubernetes
- Scrape interval: 15 seconds
- Evaluation interval: 15 seconds
- Retention: 30 days

### Grafana
- `GF_SECURITY_ADMIN_PASSWORD`: Admin password (default: admin)
- `GF_USERS_ALLOW_SIGN_UP`: Allow user signups (default: false)
- `GF_INSTALL_PLUGINS`: Additional plugins to install

## Scaling and Performance

### Horizontal Scaling

Adjust replicas in Kubernetes manifests:

```yaml
spec:
  replicas: 3  # Increase from 2
```

Apply changes:
```bash
kubectl apply -f k8s/services/bff.yaml
kubectl apply -f k8s/services/core-service.yaml
kubectl apply -f k8s/services/ui-service.yaml
```

### Resource Limits

Current configuration:
- **Requests**: 100m CPU, 128Mi Memory
- **Limits**: 500m CPU, 256Mi Memory

Adjust in `k8s/services/*.yaml` based on load testing:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Health Checks

All services include health check endpoints:

```bash
curl http://bff-service:5000/health
curl http://core-service:5001/health
curl http://ui-service:5002/health
```

Response format:
```json
{
  "status": "healthy",
  "service": "service-name",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Troubleshooting

### Services Not Starting (Docker Compose)

```bash
# Check logs
docker-compose logs -f service-name

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

### Services Not Starting (Kubernetes)

```bash
# Check pod status
kubectl get pods -n supermarket
kubectl describe pod <pod-name> -n supermarket

# View pod logs
kubectl logs <pod-name> -n supermarket

# Check events
kubectl get events -n supermarket
```

### Prometheus Not Collecting Metrics

```bash
# Verify service discovery targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090/targets

# Check ServiceMonitor/annotations on pods
kubectl describe pod <pod-name> -n supermarket
```

### Grafana Connection Issues

```bash
# Verify Prometheus service is running
kubectl get svc -n monitoring

# Check Grafana datasource configuration
# Login to Grafana → Configuration → Data Sources
# Test connection to Prometheus
```

## Production Considerations

1. **Image Registry**: Push images to private registry
2. **Secrets Management**: Use Kubernetes Secrets for sensitive data
3. **Persistent Storage**: Add PVC for Prometheus and Grafana data
4. **Backup**: Implement backup strategy for metrics and dashboards
5. **Alerting**: Configure AlertManager with notification channels
6. **Logging**: Integrate with ELK or other logging stack
7. **RBAC**: Configure fine-grained RBAC policies
8. **Network Policy**: Implement network policies
9. **TLS**: Enable HTTPS for all services
10. **Ingress**: Use Ingress controller for external access

## Development

### Adding New Metrics

Example in Python (Flask):

```python
from prometheus_client import Counter, Histogram

# Define metrics
my_counter = Counter('my_counter_total', 'Description', ['label1'])
my_histogram = Histogram('my_duration_seconds', 'Description')

# Use metrics
my_counter.labels(label1='value').inc()
with my_histogram.time():
    # Your code here
    pass
```

### Adding New Dashboard in Grafana

1. Click "+" → Create Dashboard
2. Add Panel
3. Select Prometheus datasource
4. Write PromQL query
5. Configure visualization
6. Save dashboard

### Updating Service Code

1. Modify service code in `services/<service>/main.py`
2. Rebuild image: `docker build -t supermarket/<service>:latest ./services/<service>`
3. Update Kubernetes deployment or restart Docker container

## Support and Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

## License

This project is provided as-is for learning and development purposes.
