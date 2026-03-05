variable "deployment_name" {
  description = "Deployment name"
  type        = string
  default     = "supermarket-app"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "production"
}

variable "app_replicas" {
  description = "Number of replicas for app services"
  type        = number
  default     = 2
}

variable "prometheus_replicas" {
  description = "Number of replicas for Prometheus"
  type        = number
  default     = 1
}

variable "grafana_replicas" {
  description = "Number of replicas for Grafana"
  type        = number
  default     = 1
}

variable "docker_image_prefix" {
  description = "Docker image prefix/registry"
  type        = string
  default     = ""
}

variable "resource_request_memory" {
  description = "Resource request memory"
  type        = string
  default     = "128Mi"
}

variable "resource_limit_memory" {
  description = "Resource limit memory"
  type        = string
  default     = "512Mi"
}

variable "resource_request_cpu" {
  description = "Resource request CPU"
  type        = string
  default     = "100m"
}

variable "resource_limit_cpu" {
  description = "Resource limit CPU"
  type        = string
  default     = "500m"
}

variable "enable_prometheus" {
  description = "Enable Prometheus deployment"
  type        = bool
  default     = true
}

variable "enable_grafana" {
  description = "Enable Grafana deployment"
  type        = bool
  default     = true
}

variable "enable_argocd" {
  description = "Enable ArgoCD deployment"
  type        = bool
  default     = true
}

variable "ui_node_port" {
  description = "NodePort for UI Service"
  type        = number
  default     = 30002
}

variable "grafana_node_port" {
  description = "NodePort for Grafana Service"
  type        = number
  default     = 30000
}

variable "prometheus_node_port" {
  description = "NodePort for Prometheus Service"
  type        = number
  default     = 30090
}
