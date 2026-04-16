#!/bin/bash
echo "🚀 Lancement des port-forwards..."

kubectl port-forward -n keycloak deployment/keycloak 8180:8080 &
echo "✅ Keycloak → http://localhost:8180"

kubectl port-forward svc/postgresql -n production 5433:5432 &
echo "✅ PostgreSQL → localhost:5433"

kubectl port-forward svc/vault -n vault 8200:8200 &
echo "✅ Vault → http://localhost:8200"

kubectl port-forward svc/monitoring-grafana -n monitoring 3001:80 &
echo "✅ Grafana → http://localhost:3001"

kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 &
echo "✅ Prometheus → http://localhost:9090"

echo ""
echo "✅ Tous les port-forwards sont actifs !"
echo "Pour les arrêter : kill \$(lsof -t -i:8180,5433,8200,3001,9090)"
