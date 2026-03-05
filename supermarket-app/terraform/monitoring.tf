resource "kubernetes_deployment" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = {
      app = "prometheus-server"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "prometheus-server"
      }
    }
    template {
      metadata {
        labels = {
          app = "prometheus-server"
        }
      }
      spec {
        service_account_name = kubernetes_service_account.prometheus.metadata[0].name
        container {
          name  = "prometheus"
          image = "prom/prometheus:latest"
          args = [
            "--config.file=/etc/prometheus/prometheus.yml",
            "--storage.tsdb.path=/prometheus/"
          ]
          port {
            container_port = 9090
          }
          volume_mount {
            name       = "prometheus-config-volume"
            mount_path = "/etc/prometheus/"
          }
          volume_mount {
            name       = "prometheus-storage-volume"
            mount_path = "/prometheus/"
          }
        }
        volume {
          name = "prometheus-config-volume"
          config_map {
            name = kubernetes_config_map.prometheus_config.metadata[0].name
          }
        }
        volume {
          name = "prometheus-storage-volume"
          empty_dir {}
        }
      }
    }
  }
}

resource "kubernetes_service" "prometheus" {
  metadata {
    name      = "prometheus-service"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    annotations = {
      "prometheus.io/scrape" = "true"
      "prometheus.io/port"   = "9090"
    }
  }
  spec {
    selector = {
      app = "prometheus-server"
    }
    type = "NodePort"
    port {
      port        = 9090
      target_port = 9090
      node_port   = var.prometheus_node_port
    }
  }
}

resource "kubernetes_deployment" "grafana" {
  metadata {
    name      = "grafana"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
    labels = {
      app = "grafana"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "grafana"
      }
    }
    template {
      metadata {
        labels = {
          app = "grafana"
        }
      }
      spec {
        container {
          name  = "grafana"
          image = "grafana/grafana:latest"
          port {
            container_port = 3000
          }
          env {
            name  = "GF_SECURITY_ADMIN_PASSWORD"
            value = "admin" # Change in production
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "grafana" {
  metadata {
    name      = "grafana"
    namespace = kubernetes_namespace.supermarket.metadata[0].name
  }
  spec {
    selector = {
      app = "grafana"
    }
    type = "NodePort"
    port {
      port        = 3000
      target_port = 3000
      node_port   = var.grafana_node_port
    }
  }
}
