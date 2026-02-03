#!/usr/bin/env bash
# Import the sample Grafana dashboard into Grafana using admin/admin
GRAFANA_URL=${GRAFANA_URL:-http://localhost:3000}
DASHBOARD_FILE="$(dirname "$0")/supermarket-dashboard.json"
if [ ! -f "$DASHBOARD_FILE" ]; then
  echo "Dashboard file not found: $DASHBOARD_FILE"
  exit 1
fi

echo "Waiting for Grafana to become available at $GRAFANA_URL..."
for i in {1..30}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$GRAFANA_URL") || true
  if [ "$status" = "200" ]; then
    echo "Grafana reachable"
    break
  fi
  sleep 2
done

echo "Importing dashboard..."
curl -s -X POST "$GRAFANA_URL/api/dashboards/db" -u admin:admin -H "Content-Type: application/json" -d @"$DASHBOARD_FILE" | jq .
