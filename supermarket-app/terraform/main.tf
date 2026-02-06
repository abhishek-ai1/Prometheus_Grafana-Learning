# Terraform configuration for Supermarket App Kubernetes Infrastructure
# This creates a complete K8s environment with Minikube on local machine

terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
  config_context = var.k8s_context
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
    config_context = var.k8s_context
  }
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "k8s_context" {
  description = "Kubernetes context to use"
  type        = string
  default     = "minikube"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "supermarket"
}

variable "docker_registry" {
  description = "Docker registry for images"
  type        = string
  default     = "localhost:5000"
}

# Create Namespace
resource "kubernetes_namespace" "supermarket" {
  metadata {
    name = var.namespace
    labels = {
      name = var.namespace
    }
  }
}

# Create ConfigMaps
resource "kubernetes_config_map" "auth_service_config" {
  metadata {
    name      = "auth-service-config"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }

  data = {
    SECRET_KEY  = "your-secret-key-change-in-production"
    ENVIRONMENT = "production"
  }
}

resource "kubernetes_config_map" "bff_service_config" {
  metadata {
    name      = "bff-service-config"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }

  data = {
    ENVIRONMENT           = "production"
    AUTH_SERVICE_URL      = "http://auth-service:5003"
    CUSTOMER_MGMT_URL     = "http://customer-mgmt:5004"
    CORE_SERVICE_URL      = "http://core-service:5001"
  }
}

resource "kubernetes_config_map" "customer_mgmt_config" {
  metadata {
    name      = "customer-mgmt-config"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }

  data = {
    ENVIRONMENT      = "production"
    AUTH_SERVICE_URL = "http://auth-service:5003"
  }
}

resource "kubernetes_config_map" "core_service_config" {
  metadata {
    name      = "core-service-config"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }

  data = {
    ENVIRONMENT = "production"
  }
}

resource "kubernetes_config_map" "ui_service_config" {
  metadata {
    name      = "ui-service-config"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }

  data = {
    ENVIRONMENT    = "production"
    # UI connects to BFF
    API_BASE_URL   = "http://bff-service:5000"
    BFF_SERVICE_URL = "http://bff-service:5000"
  }
}

# ================= APPS =================

# --- Auth Service ---
resource "kubernetes_deployment" "auth_service" {
  metadata {
    name      = "auth-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = { app = "auth-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "auth-service" } }
    template {
      metadata {
        labels = { app = "auth-service" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5003"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        container {
          image = "supermarket/auth-service:latest"
          name  = "auth-service"
          image_pull_policy = "IfNotPresent"
          port { container_port = 5003 }
          env_from {
            config_map_ref { name = kubernetes_config_map.auth_service_config.metadata[0].name }
          }
          liveness_probe {
            http_get { path = "/health"; port = 5003 }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "auth_service" {
  metadata {
    name      = "auth-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = { app = "auth-service" }
    port {
      port        = 5003
      target_port = 5003
    }
    type = "ClusterIP"
  }
}

# --- Core Service ---
resource "kubernetes_deployment" "core_service" {
  metadata {
    name      = "core-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = { app = "core-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "core-service" } }
    template {
      metadata {
        labels = { app = "core-service" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5001"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        container {
          image = "supermarket/core-service:latest"
          name  = "core-service"
          image_pull_policy = "IfNotPresent"
          port { container_port = 5001 }
          env_from {
            config_map_ref { name = kubernetes_config_map.core_service_config.metadata[0].name }
          }
          liveness_probe {
            http_get { path = "/health"; port = 5001 }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "core_service" {
  metadata {
    name      = "core-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = { app = "core-service" }
    port {
      port        = 5001
      target_port = 5001
    }
    type = "ClusterIP"
  }
}

# --- Customer Mgmt ---
resource "kubernetes_deployment" "customer_mgmt" {
  metadata {
    name      = "customer-mgmt"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = { app = "customer-mgmt" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "customer-mgmt" } }
    template {
      metadata {
        labels = { app = "customer-mgmt" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5004"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        container {
          image = "supermarket/customer-mgmt:latest"
          name  = "customer-mgmt"
          image_pull_policy = "IfNotPresent"
          port { container_port = 5004 }
          env_from {
            config_map_ref { name = kubernetes_config_map.customer_mgmt_config.metadata[0].name }
          }
          liveness_probe {
            http_get { path = "/health"; port = 5004 }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "customer_mgmt" {
  metadata {
    name      = "customer-mgmt"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = { app = "customer-mgmt" }
    port {
      port        = 5004
      target_port = 5004
    }
    type = "ClusterIP"
  }
}

# --- BFF Service ---
resource "kubernetes_deployment" "bff_service" {
  metadata {
    name      = "bff-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = { app = "bff" }
  }
  spec {
    replicas = 2
    selector { match_labels = { app = "bff" } }
    template {
      metadata {
        labels = { app = "bff" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5000"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        container {
          image = "supermarket/bff:latest"
          name  = "bff"
          image_pull_policy = "IfNotPresent"
          port { container_port = 5000 }
          env_from {
            config_map_ref { name = kubernetes_config_map.bff_service_config.metadata[0].name }
          }
          liveness_probe {
            http_get { path = "/health"; port = 5000 }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "bff_service" {
  metadata {
    name      = "bff-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = { app = "bff" }
    port {
      port        = 5000
      target_port = 5000
    }
    type = "LoadBalancer"
  }
}

# --- UI Service ---
resource "kubernetes_deployment" "ui_service" {
  metadata {
    name      = "ui-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = { app = "ui-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "ui-service" } }
    template {
      metadata {
        labels = { app = "ui-service" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5002"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        container {
          image = "supermarket/ui-service:latest"
          name  = "ui-service"
          image_pull_policy = "IfNotPresent"
          port { container_port = 5002 }
          env_from {
            config_map_ref { name = kubernetes_config_map.ui_service_config.metadata[0].name }
          }
          liveness_probe {
            http_get { path = "/health"; port = 5002 }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "ui_service" {
  metadata {
    name      = "ui-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = { app = "ui-service" }
    type = "NodePort"
    port {
      port        = 5002
      target_port = 5002
      node_port   = var.ui_node_port
    }
  }
}

# Create ConfigMap for Prometheus
resource "kubernetes_config_map" "prometheus_config" {
  metadata {
    name      = "prometheus-server-conf"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  
  data = {
    "prometheus.yml" = <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__meta_kubernetes_address, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
    - action: labelmap
      regex: __meta_kubernetes_pod_label_(.+)
    - source_labels: [__meta_kubernetes_namespace]
      action: replace
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_pod_name]
      action: replace
      target_label: kubernetes_pod_name
EOF
  }
}

# Create ServiceAccount for Prometheus
resource "kubernetes_service_account" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
}

# Create ClusterRole for Prometheus
resource "kubernetes_cluster_role" "prometheus" {
  metadata {
    name = "prometheus"
  }

  rule {
    api_groups = [""]
    resources  = ["nodes", "nodes/proxy", "services", "endpoints", "pods"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["extensions"]
    resources  = ["ingresses"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    non_resource_urls = ["/metrics"]
    verbs             = ["get"]
  }
}

# Create ClusterRoleBinding for Prometheus
resource "kubernetes_cluster_role_binding" "prometheus" {
  metadata {
    name = "prometheus"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.prometheus.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.prometheus.metadata[0].name
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
}

# Outputs
output "namespace" {
  value       = kubernetes_namespace.supermarket.metadata[0].name
  description = "Kubernetes namespace"
}
