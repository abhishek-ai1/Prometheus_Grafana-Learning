# Quick Reference Guide

Fast lookup guide for common commands and configurations.

## Quick Start (Local)

```bash
# Navigate to project
cd supermarket-app

# Start stack (Docker Compose)
chmod +x run-local.sh
./run-local.sh

# Stop stack
chmod +x stop-local.sh
./stop-local.sh

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build
```

## Quick Start (Kubernetes)

```bash
# Build images
chmod +x build-images.sh
./build-images.sh

# Deploy
chmod +x deploy-k8s.sh
./deploy-k8s.sh

# Check status
kubectl get pods -n supermarket
kubectl get pods -n monitoring

# Port forward to services
kubectl port-forward -n supermarket svc/ui-service 5002:5002
kubectl port-forward -n monitoring svc/grafana 3000:3000
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

## Service URLs

### Local Development
| Service | URL |
|---------|-----|
| UI | http://localhost:5002 |
| BFF API | http://localhost:5000 |
| Core API | http://localhost:5001 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

### Kubernetes (with port-forward)
Same as above after running port-forward commands

## Health Check Commands

```bash
# All services
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health

# Kubernetes services (from another pod)
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://bff-service:5000/health -n supermarket
```

## API Quick Reference

### Products API

```bash
# Get all products (via BFF)
curl http://localhost:5000/api/products

# Get specific product
curl http://localhost:5000/api/products/1

# Get all products (Core Service)
curl http://localhost:5001/products

# Create product
curl -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Item","price":9.99,"category":"Category"}'
```

### Orders API

```bash
# Create order
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id":"1","name":"Milk","price":3.99,"quantity":1}
    ]
  }'

# Get order
curl http://localhost:5000/api/orders/order_id

# Update order status (Core Service)
curl -X PUT http://localhost:5001/orders/order_id/status \
  -H "Content-Type: application/json" \
  -d '{"status":"shipped"}'
```

## Metrics & Monitoring

### Access Metrics Endpoints

```bash
# BFF Service metrics
curl http://localhost:5000/metrics

# Core Service metrics
curl http://localhost:5001/metrics

# UI Service metrics
curl http://localhost:5002/metrics
```

### Common Prometheus Queries

```promql
# Request rate (req/s)
rate(bff_requests_total[5m])

# Average latency (ms)
avg(bff_request_duration_seconds) * 1000

# Orders per minute
sum(rate(orders_created_total[1m])) * 60

# Error rate
rate(bff_requests_total{status=~"5.."}[5m])

# Latency percentiles
histogram_quantile(0.95, rate(bff_request_duration_seconds_bucket[5m]))
```

### Grafana Access

```
URL: http://localhost:3000
Username: admin
Password: admin
```

## Docker Compose Commands

```bash
# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Rebuild images
docker-compose build

# Remove volumes (data)
docker-compose down -v

# Check container status
docker-compose ps

# Rebuild and start
docker-compose up -d --build
```

## Kubernetes Commands

### Namespace Management

```bash
# List all namespaces
kubectl get namespaces

# Get resources in namespace
kubectl get all -n supermarket
kubectl get all -n monitoring

# Describe namespace
kubectl describe namespace supermarket
```

### Pod Management

```bash
# List pods
kubectl get pods -n supermarket
kubectl get pods -n monitoring

# Describe pod
kubectl describe pod <pod_name> -n supermarket

# View logs
kubectl logs <pod_name> -n supermarket

# Execute command
kubectl exec -it <pod_name> -n supermarket -- bash

# Port forward
kubectl port-forward <pod_name> 5000:5000 -n supermarket
```

### Service Management

```bash
# List services
kubectl get svc -n supermarket
kubectl get svc -n monitoring

# Describe service
kubectl describe svc <service_name> -n supermarket

# Get service endpoints
kubectl get endpoints -n supermarket

# Port forward to service
kubectl port-forward svc/<service_name> 5000:5000 -n supermarket
```

### Deployment Management

```bash
# List deployments
kubectl get deployments -n supermarket

# Describe deployment
kubectl describe deployment <deployment_name> -n supermarket

# Scale deployment
kubectl scale deployment <deployment_name> --replicas=3 -n supermarket

# Set image
kubectl set image deployment/<deployment_name> \
  <container_name>=<new_image> -n supermarket

# Rollout status
kubectl rollout status deployment/<deployment_name> -n supermarket

# Rollback
kubectl rollout undo deployment/<deployment_name> -n supermarket
```

### Troubleshooting

```bash
# View all events
kubectl get events -n supermarket

# Top resources usage
kubectl top nodes
kubectl top pods -n supermarket

# Debug pod
kubectl run -it --rm debug --image=busybox --restart=Never -- sh

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://bff-service:5000/health
```

## File Locations

| Component | File |
|-----------|------|
| BFF Service | `services/bff/` |
| Core Service | `services/core-service/` |
| UI Service | `services/ui-service/` |
| K8s Services | `k8s/services/*.yaml` |
| Prometheus | `k8s/monitoring/prometheus.yaml` |
| Grafana | `k8s/monitoring/grafana.yaml` |
| Dashboard | `k8s/dashboard/` |
| Docker Compose | `docker-compose.yml` |
| Docs | `README.md`, `*.md` |

## Common Issues & Fixes

### Services not starting (Docker)

```bash
# Check logs
docker-compose logs service_name

# Rebuild
docker-compose build service_name
docker-compose up -d service_name
```

### Services not starting (K8s)

```bash
# Check logs
kubectl logs <pod_name> -n supermarket

# Describe pod for events
kubectl describe pod <pod_name> -n supermarket

# Check resource availability
kubectl describe nodes
```

### No metrics in Prometheus

```bash
# Check targets
# Visit http://localhost:9090/targets

# Verify endpoint
curl http://localhost:5000/metrics

# Check pod annotations
kubectl describe pod <pod_name> -n supermarket
```

### Grafana can't connect to Prometheus

```bash
# Check Prometheus status
kubectl get pods -n monitoring

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://prometheus:9090
```

## Environment Variables

### Docker Compose

```bash
# In docker-compose.yml
environment:
  - ENVIRONMENT=development
  - API_BASE_URL=http://bff-service:5000
```

### Kubernetes

```bash
# In YAML deployment
env:
  - name: ENVIRONMENT
    value: "production"
  - name: API_BASE_URL
    value: "http://bff-service:5000"
```

## Resource Requests/Limits

Current defaults:
- **CPU Request**: 100m
- **Memory Request**: 128Mi
- **CPU Limit**: 500m
- **Memory Limit**: 256Mi

To modify, edit `k8s/services/*.yaml`:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Port Mapping

| Service | Port | Container | Type |
|---------|------|-----------|------|
| BFF | 5000 | 5000 | HTTP |
| Core Service | 5001 | 5001 | HTTP |
| UI Service | 5002/80 | 5002 | HTTP |
| Prometheus | 9090 | 9090 | HTTP |
| Grafana | 3000 | 3000 | HTTP |
| K8s Dashboard | 8443 | 8443 | HTTPS |

## Database Files (Local)

Persisted in Docker volumes:
- `prometheus-storage`: Prometheus time-series data
- `grafana-storage`: Grafana dashboards and configuration

To reset:
```bash
docker volume rm supermarket-app_prometheus-storage
docker volume rm supermarket-app_grafana-storage
```

## Documentation Files

| Document | Purpose |
|----------|---------|
| README.md | Overview and quick start |
| DEPLOYMENT_GUIDE.md | Complete deployment instructions |
| KUBERNETES_DASHBOARD.md | K8s Dashboard setup and usage |
| PROMETHEUS_GRAFANA.md | Monitoring stack detailed guide |
| API_DOCUMENTATION.md | API endpoints and usage |
| QUICK_REFERENCE.md | This file |

## Building Custom Dashboards (Grafana)

1. Go to http://localhost:3000
2. **+** → **Dashboard**
3. **Add Panel**
4. Select **Prometheus** datasource
5. Write PromQL query
6. **Save**

Example queries:
```promql
rate(bff_requests_total[5m])
histogram_quantile(0.95, bff_request_duration_seconds_bucket)
orders_created_total
```

## Kubernetes Dashboard Access

```bash
# Get token
kubectl -n kubernetes-dashboard create token admin-user

# Port forward
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 8443:443

# Access
https://localhost:8443

# Login with token
```

## Scaling Services

```bash
# Docker Compose (edit docker-compose.yml)
deploy:
  replicas: 3

# Kubernetes
kubectl scale deployment bff-service --replicas=3 -n supermarket
```

## Useful Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias sm-start='cd supermarket-app && ./run-local.sh'
alias sm-stop='cd supermarket-app && ./stop-local.sh'
alias sm-logs='docker-compose logs -f'
alias k-sm='kubectl -n supermarket'
alias k-mon='kubectl -n monitoring'
alias prom-fwd='kubectl port-forward -n monitoring svc/prometheus 9090:9090'
alias graf-fwd='kubectl port-forward -n monitoring svc/grafana 3000:3000'
```

## Performance Metrics

Monitor these key metrics:

```promql
# Throughput (requests/sec)
sum(rate(bff_requests_total[5m]))

# Latency (ms)
avg(bff_request_duration_seconds) * 1000

# Error rate (%)
(sum(rate(bff_requests_total{status=~"5.."}[5m])) / sum(rate(bff_requests_total[5m]))) * 100

# Orders (per minute)
sum(rate(orders_created_total[1m])) * 60
```

## References

- [Official Kubernetes Docs](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [Docker Docs](https://docs.docker.com/)
- [Flask Docs](https://flask.palletsprojects.com/)
