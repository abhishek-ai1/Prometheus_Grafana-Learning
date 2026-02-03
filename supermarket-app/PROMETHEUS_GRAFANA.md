# Prometheus & Grafana Setup Guide

## Overview

This guide covers the Prometheus and Grafana monitoring stack for the Supermarket microservices application. We've also integrated a built-in **System Monitoring Dashboard** in the application UI for easy access to service health and metrics.

## Quick Access to Monitoring

### In-App Monitoring Dashboard

The application includes a professional **System Monitoring Dashboard** with real-time service status and metrics:

```
Access: http://localhost:5002/monitoring
```

**Features:**
- Real-time service health status (BFF, Core, UI, Prometheus, Grafana)
- Live metrics visualization with charts
- Request rate graphs
- Response time distribution
- API endpoint status overview
- Auto-refresh every 30 seconds

**What You Can See:**
- ✅ Service status indicators (Healthy/Unhealthy)
- 📊 Request rate trends
- ⏱️ Response time metrics
- 🔗 Available API endpoints
- 📈 System statistics (total requests, average response time, active connections)

### External Monitoring Tools

- **Prometheus**: http://localhost:9090 - Raw metrics queries and graphs
- **Grafana**: http://localhost:3000 - Professional dashboards and visualizations

## Prometheus Setup

### Configuration

Prometheus is configured via ConfigMap: `prometheus-config`

**Key Settings:**
- **Scrape Interval**: 15 seconds
- **Evaluation Interval**: 15 seconds
- **Retention**: 30 days
- **Storage**: 50GB (configurable)

### Service Discovery

Prometheus uses Kubernetes service discovery to automatically find and scrape metrics from pods with annotations:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "5000"
    prometheus.io/path: "/metrics"
```

### Scrape Targets

Automatically discovered targets:

| Target | Port | Path |
|--------|------|------|
| BFF Service | 5000 | /metrics |
| Core Service | 5001 | /metrics |
| UI Service | 5002 | /metrics |
| Kubernetes API | 6443 | /metrics |
| Kubernetes Nodes | 10250 | /metrics |
| Kubernetes Pods | - | /metrics |

### Accessing Prometheus

```bash
# Local development
http://localhost:9090

# Kubernetes (port-forward)
kubectl port-forward -n monitoring svc/prometheus 9090:9090
http://localhost:9090
```

### Prometheus UI Features

1. **Graph Tab**: Query metrics and visualize
2. **Alerts Tab**: View active alerts
3. **Status Tab**: Check configuration and targets
4. **Targets Page** (`http://localhost:9090/targets`): View scrape targets and status

### Example Queries

#### Request Rate (Requests per Second)

```promql
# BFF Service request rate
rate(bff_requests_total[5m])

# All services combined
sum(rate(bff_requests_total[5m]) + rate(core_service_requests_total[5m]) + rate(ui_service_requests_total[5m]))
```

#### Request Duration

```promql
# Average request duration (BFF)
avg(bff_request_duration_seconds)

# 95th percentile request duration (Core Service)
histogram_quantile(0.95, rate(core_service_request_duration_seconds_bucket[5m]))
```

#### Orders Created

```promql
# Orders per second
rate(orders_created_total[5m])

# Total orders created
orders_created_total
```

#### Error Rates

```promql
# HTTP errors (5xx)
rate(http_requests_total{status=~"5.."}[5m])

# Error ratio
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

## Grafana Setup

### Default Credentials
- **Username**: admin
- **Password**: admin

### Access Grafana

```bash
# Local development
http://localhost:3000

# Kubernetes (port-forward)
kubectl port-forward -n monitoring svc/grafana 3000:3000
http://localhost:3000
```

### Initial Setup

1. Log in with default credentials (admin/admin)
2. Change admin password (recommended)
3. Configure Prometheus datasource (should be pre-configured)

### Datasources

Grafana uses Prometheus as the primary datasource.

**Datasource Configuration:**
- Name: Prometheus
- URL: http://prometheus:9090
- Access: Server (default)
- Scrape interval: 15s

Verify datasource:
1. Go to **Configuration** → **Data Sources**
2. Click **Prometheus**
3. Click **Save & Test**

### Pre-configured Dashboards

#### Supermarket System Overview

Displays:
- Total request rate
- Average request duration
- Orders created
- Products queried

**Access:**
1. Go to **Dashboards** → **Browse**
2. Select "Supermarket System Overview"

### Creating Custom Dashboards

#### 1. Create Dashboard

- Click **+** → **Dashboard**
- Click **Add Panel**
- Select Prometheus datasource

#### 2. Add Panels

**Panel: Request Rate**
- Title: "Request Rate (req/s)"
- Query: `sum(rate(bff_requests_total[5m]) + rate(core_service_requests_total[5m]) + rate(ui_service_requests_total[5m]))`
- Visualization: Graph

**Panel: Service Latency**
- Title: "Request Latency (ms)"
- Query: `avg(bff_request_duration_seconds) * 1000`
- Visualization: Graph

**Panel: Orders Created**
- Title: "Orders Created"
- Query: `sum(rate(orders_created_total[5m]))`
- Visualization: Gauge

#### 3. Configure Visualization

- Panel Title
- Graph type (line, bar, gauge, etc.)
- Legend (show/hide)
- Thresholds (optional)
- Color scheme

#### 4. Save Dashboard

- Click **Save** (top right)
- Name: "Supermarket Custom Dashboard"
- Folder: "General"
- Tags: supermarket, custom

### Dashboard Examples

#### Service Health Dashboard

```promql
# BFF Service Health
(1 - rate(bff_core_service_calls_total{outcome="error"}[5m])) * 100

# Core Service Health
(1 - rate(core_service_requests_total{status=~"5.."}[5m])) * 100

# UI Service Health
(1 - rate(ui_service_requests_total{status=~"5.."}[5m])) * 100
```

#### Performance Dashboard

```promql
# P95 Latency
histogram_quantile(0.95, rate(bff_request_duration_seconds_bucket[5m])) * 1000

# P99 Latency
histogram_quantile(0.99, rate(bff_request_duration_seconds_bucket[5m])) * 1000

# Max Latency
max(bff_request_duration_seconds) * 1000
```

#### Business Metrics Dashboard

```promql
# Orders per minute
sum(rate(orders_created_total[1m])) * 60

# Total orders
orders_created_total

# Product searches per minute
sum(rate(products_queried_total[1m])) * 60
```

### Alerting (Grafana)

#### Setup Alert Notification Channel

1. Go to **Alerting** → **Notification channels**
2. Click **New channel**
3. Select type (Email, Slack, PagerDuty, etc.)
4. Configure settings
5. Click **Save**

#### Create Alert Rule

1. Open dashboard panel
2. Click **Alert** tab
3. Set conditions:
   - Evaluator: (is above, is below, etc.)
   - Threshold value
   - For: (time window)
4. Configure notifications
5. Click **Save**

**Example Alert:**
- Query: `rate(bff_requests_total{status=~"5.."}[5m])`
- Condition: Is above 0.1
- For: 5 minutes
- Message: "High error rate detected"

## Advanced Prometheus Queries

### Multi-service Comparison

```promql
# Request rate by service
sum by (job) (rate(bff_requests_total[5m]))
```

### Percentile Analysis

```promql
# 50th, 95th, 99th percentile latency
histogram_quantile(0.50, rate(bff_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(bff_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(bff_request_duration_seconds_bucket[5m]))
```

### Error Rate Calculation

```promql
# Error ratio as percentage
(sum(rate(bff_requests_total{status=~"5.."}[5m])) / sum(rate(bff_requests_total[5m]))) * 100
```

### Resource Usage

```promql
# Pod CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Pod memory usage
container_memory_usage_bytes / 1024 / 1024
```

## Storage Management

### Retention Policy

Current retention: 30 days

To modify:
```bash
# Edit Prometheus deployment
kubectl edit deployment prometheus -n monitoring

# Change flag in args:
# --storage.tsdb.retention.time=30d
```

### Storage Size

Monitor storage usage:
```promql
# TSDB size
prometheus_tsdb_symbol_table_size_bytes
prometheus_tsdb_index_chunk_l1_mmappings_total
```

## Troubleshooting

### Prometheus Issues

**Targets showing as DOWN**

```bash
# Check prometheus logs
kubectl logs deployment/prometheus -n monitoring

# Verify pod annotations
kubectl describe pod <pod-name> -n supermarket

# Check network connectivity
kubectl exec -it <prometheus-pod> -n monitoring -- bash
curl http://bff-service:5000/metrics -v
```

**No metrics collected**

```bash
# Verify service is running and exposing metrics
curl http://localhost:5000/metrics

# Check Prometheus targets page
http://localhost:9090/targets
```

**High memory usage**

```yaml
# Reduce retention period
--storage.tsdb.retention.time=7d

# Reduce scrape frequency
global:
  scrape_interval: 30s
```

### Grafana Issues

**Cannot connect to Prometheus**

1. Check datasource configuration
2. Verify Prometheus service is running
3. Check network connectivity between pods

**Dashboard panels empty**

1. Verify metrics are being collected (check Prometheus)
2. Check PromQL query syntax
3. Verify time range includes data points

**Alerts not firing**

1. Check alert condition in panel
2. Verify notification channel is configured
3. Check logs for evaluation errors

## Performance Optimization

### Prometheus

```yaml
# Increase resource limits
resources:
  limits:
    memory: 2Gi
    cpu: 2000m

# Add persistent volume for data
volumeMounts:
  - name: prometheus-storage
    mountPath: /prometheus

# Use read-only replicas for high traffic
replicas: 2
```

### Grafana

```yaml
# Enable caching
env:
  - name: GF_QUERY_TIMEOUT
    value: "30s"
```

## Backup and Restore

### Backup Prometheus Data

```bash
# Create backup
kubectl exec -it <prometheus-pod> -n monitoring -- \
  tar czf /tmp/prometheus-backup.tar.gz /prometheus

# Copy to local
kubectl cp monitoring/<prometheus-pod>:/tmp/prometheus-backup.tar.gz \
  ./prometheus-backup.tar.gz
```

### Backup Grafana Dashboards

```bash
# Export dashboard as JSON
# Go to Dashboard settings → Export → Save JSON
```

## Resources and References

- [Prometheus Official Documentation](https://prometheus.io/docs/)
- [Grafana Official Documentation](https://grafana.com/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Grafana Alerts](https://grafana.com/docs/grafana/latest/alerting/)
