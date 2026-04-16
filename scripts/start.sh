#!/bin/bash

echo "🚀 Démarrage du projet Investissement..."

# 1. Vérifie que Docker Desktop tourne
echo "⏳ Vérification de Docker..."
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker Desktop n'est pas démarré !"
  echo "👉 Lance Docker Desktop et relance ce script."
  exit 1
fi
echo "✅ Docker Desktop est actif"

# 2. Démarre Minikube si arrêté
echo "⏳ Vérification de Minikube..."
MINIKUBE_STATUS=$(minikube status --format='{{.Host}}' 2>/dev/null)
if [ "$MINIKUBE_STATUS" != "Running" ]; then
  echo "⏳ Démarrage de Minikube..."
  minikube start --driver=docker
else
  echo "✅ Minikube est déjà actif"
fi

# 3. Attend que tous les pods soient Ready
echo "⏳ Attente des pods Kubernetes..."
kubectl wait --for=condition=Ready pods --all -n production --timeout=120s 2>/dev/null
kubectl wait --for=condition=Ready pods --all -n keycloak --timeout=120s 2>/dev/null
echo "✅ Tous les pods sont prêts"

# 4. Tue les anciens port-forwards
echo "⏳ Nettoyage des anciens port-forwards..."
kill $(lsof -t -i:8180) 2>/dev/null
kill $(lsof -t -i:5433) 2>/dev/null
kill $(lsof -t -i:8200) 2>/dev/null
kill $(lsof -t -i:3001) 2>/dev/null
kill $(lsof -t -i:9090) 2>/dev/null
sleep 2

# 5. Lance les port-forwards
echo "⏳ Lancement des port-forwards..."
kubectl port-forward -n keycloak deployment/keycloak 8180:8080 > /dev/null 2>&1 &
kubectl port-forward svc/postgresql -n production 5433:5432 > /dev/null 2>&1 &
kubectl port-forward svc/vault -n vault 8200:8200 > /dev/null 2>&1 &
kubectl port-forward svc/monitoring-grafana -n monitoring 3001:80 > /dev/null 2>&1 &
kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 > /dev/null 2>&1 &
sleep 3
echo "✅ Port-forwards actifs"

# 6. Réinitialise les secrets Vault
echo "⏳ Initialisation des secrets Vault..."
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='root'
vault secrets enable -path=mon-projet kv-v2 > /dev/null 2>&1
vault kv put mon-projet/backend \
  django_secret_key='change-me-super-secret-key-2026' \
  django_debug='False' \
  django_allowed_hosts='app.local,localhost' > /dev/null 2>&1
vault kv put mon-projet/database \
  db_name='monprojet' \
  db_user='admin' \
  db_password='SuperSecret2026!' > /dev/null 2>&1
echo "✅ Secrets Vault initialisés"

# 7. Lance docker-compose
echo "⏳ Démarrage des services docker-compose..."
docker-compose up -d 2>&1 | grep -v "keycloak"
echo "✅ Services démarrés"

# 8. Affiche le résumé
echo ""
echo "════════════════════════════════════════"
echo "✅ Projet Investissement démarré !"
echo "════════════════════════════════════════"
echo ""
echo "🌐 Frontend     → http://localhost:3000"
echo "🔧 Backend      → http://localhost:8000"
echo "🔐 Keycloak     → http://localhost:8180"
echo "📊 Grafana      → http://localhost:3001"
echo "🔍 Prometheus   → http://localhost:9090"
echo "🔒 Vault        → http://localhost:8200"
echo "🗄️  PostgreSQL   → localhost:5433"
echo ""
echo "👤 Login : testuser / Test2026!"
echo "👤 Admin : admin / Admin2026!Secure"
echo "════════════════════════════════════════"
