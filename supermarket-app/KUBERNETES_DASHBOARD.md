# Kubernetes Dashboard Setup Guide

## Overview

The Kubernetes Dashboard is a web-based Kubernetes user interface that allows you to deploy containerized applications, troubleshoot them, and manage the cluster resources.

## Features

- **Cluster Overview**: View overall cluster health and resource usage
- **Workload Management**: Manage deployments, pods, services, and other resources
- **Monitoring**: View resource usage and metrics
- **Logs**: Access container logs
- **Terminal Access**: Execute commands in containers
- **RBAC**: Role-based access control

## Installation (Automated)

The dashboard is automatically set up with the main deployment:

```bash
./deploy-k8s.sh
```

This creates:
- `kubernetes-dashboard` namespace
- Service account: `admin-user`
- ClusterRoleBinding for admin access
- LoadBalancer service for external access

## Manual Installation

### 1. Install Official Dashboard (Optional)

If you want the official Kubernetes Dashboard:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

### 2. Get Admin Token

```bash
# Get token for authentication
kubectl -n kubernetes-dashboard create token admin-user

# Or get long-lived token
kubectl -n kubernetes-dashboard get secret admin-user-token -o jsonpath={".data.token"} | base64 -d
```

## Accessing the Dashboard

### Method 1: Port Forwarding

```bash
# Forward dashboard port
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 8443:443

# Access in browser
https://localhost:8443

# Paste the token from above
```

### Method 2: kubectl proxy

```bash
kubectl proxy

# Access at http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### Method 3: LoadBalancer (if available)

```bash
# Get LoadBalancer IP/hostname
kubectl get svc -n kubernetes-dashboard

# Access via LoadBalancer (if EXTERNAL-IP is available)
https://<EXTERNAL-IP>:8443
```

## Usage Examples

### Viewing Supermarket Namespace

1. Navigate to dashboard
2. Select "supermarket" namespace from dropdown
3. View all resources:
   - Deployments
   - Pods
   - Services
   - ConfigMaps

### Monitoring Resources

1. Go to **Workloads** → **Deployments**
2. Click on service name to view details
3. See:
   - Pod replicas status
   - CPU/Memory usage
   - Events and logs

### Viewing Logs

1. Go to **Workloads** → **Pods**
2. Click on pod name
3. Click **Logs** tab
4. View real-time logs from container

### Accessing Container Terminal

1. Go to **Workloads** → **Pods**
2. Click on pod
3. Click **Exec** icon
4. Run shell commands in container

### Scaling Deployments

1. Go to **Workloads** → **Deployments**
2. Click deployment name
3. Edit replica count
4. Changes apply immediately

## RBAC and Access Control

The setup includes:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

This grants admin access to the `admin-user` service account.

### Creating Limited Access Users

For specific namespaces:

```bash
# Create service account
kubectl create serviceaccount limited-user -n supermarket

# Create role with limited permissions
kubectl create role pod-reader --verb=get --verb=list --resource=pods -n supermarket

# Bind role to service account
kubectl create rolebinding pod-reader-binding --clusterrole=pod-reader --serviceaccount=supermarket:limited-user -n supermarket

# Get token for limited user
kubectl -n supermarket create token limited-user
```

## Dashboard Customization

### Dark Mode

Available in dashboard settings (user profile → preferences)

### Namespace Selection

Default view shows all namespaces. Select specific namespace from dropdown to focus.

### Favorite Resources

Pin frequently accessed resources for quick access.

## Troubleshooting

### Dashboard Pod Crashing

```bash
kubectl describe pod -n kubernetes-dashboard
kubectl logs -n kubernetes-dashboard deployment/kubernetes-dashboard
```

### Token Expiration

Tokens expire after 1 hour. Get new token:

```bash
kubectl -n kubernetes-dashboard create token admin-user
```

### Permission Denied Errors

Verify RBAC:

```bash
kubectl get rolebindings -n kubernetes-dashboard
kubectl get clusterrolebindings | grep admin-user
```

### Cannot Access via LoadBalancer

Check if LoadBalancer service has external IP:

```bash
kubectl get svc -n kubernetes-dashboard
# EXTERNAL-IP should not be <pending>
```

For local clusters (minikube/k3s), use port-forward instead.

## Security Best Practices

1. **Use Token Authentication**: Always authenticate with token
2. **Limit User Access**: Create specific roles for different teams
3. **HTTPS Only**: Dashboard uses HTTPS for communication
4. **Network Policy**: Restrict access to dashboard network
5. **Audit Logging**: Enable audit logs for cluster changes
6. **Regular Backups**: Backup cluster configuration

## Integration with Prometheus/Grafana

While Kubernetes Dashboard provides basic metrics, use Grafana for:
- Custom dashboards
- Historical data analysis
- Complex queries
- Automated alerting

Access Grafana via:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

## Additional Resources

- [Official Kubernetes Dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)
- [Dashboard GitHub Repository](https://github.com/kubernetes/dashboard)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
