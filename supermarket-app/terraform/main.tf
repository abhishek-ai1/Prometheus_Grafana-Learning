# Terraform configuration for Supermarket App Kubernetes Infrastructure
# This creates a complete K8s environment with Minikube on local machine
#
# Prerequisites:
#   - Terraform installed
#   - Docker installed
#   - minikube installed
#
# Usage:
#   terraform init
#   terraform plan
#   terraform apply
#   terraform destroy (to clean up)

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
    API_BASE_URL   = "http://bff-service:5000"
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

output "kubeconfig_path" {
  value       = var.kubeconfig_path
  description = "Path to kubeconfig"
}

output "k8s_context" {
  value       = var.k8s_context
  description = "Kubernetes context"
}
