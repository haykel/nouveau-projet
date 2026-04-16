# CLAUDE.md - Instructions d'installation DevOps

Ce fichier contient toutes les commandes pour déployer l'architecture DevOps complète du projet mon-projet-devops sur un Mac Apple Silicon M4.

## 1. Installation des outils (Homebrew)

```bash
brew install minikube kubectl helm vault trivy
```

## 2. Demarrage Minikube (ARM64 / Apple Silicon M4)

```bash
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=10240 \
  --kubernetes-version=v1.31.0
```

> **Fix applique** : `--memory=10240` est necessaire pour supporter kube-prometheus-stack + Loki + Vault + ArgoCD simultanement. Valeur par defaut (2048) insuffisante.

Activer l'ingress controller :

```bash
minikube addons enable ingress
```

## 3. Installation ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Attendre que les pods soient prets :

```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s
```

Recuperer le mot de passe admin :

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Port-forward pour acceder a l'UI :

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## 4. Installation Vault

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

kubectl create namespace vault

helm install vault hashicorp/vault \
  --namespace vault \
  --set "server.dev.enabled=true" \
  --set "server.dev.devRootToken=root"
```

Creation des secrets :

```bash
kubectl exec -n vault vault-0 -- vault kv put secret/django \
  SECRET_KEY="your-production-secret-key" \
  DEBUG="false" \
  ALLOWED_HOSTS="app.local"

kubectl exec -n vault vault-0 -- vault kv put secret/sonarqube \
  monitoringPasscode="your-sonarqube-passcode"
```

> **Fix applique** : `monitoringPasscode` est requis pour le webhook SonarQube. Le configurer dans les secrets Vault.

## 5. Installation kube-prometheus-stack (Grafana, Prometheus, Alertmanager)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin \
  --set grafana.sidecar.datasources.enabled=true \
  --set grafana.sidecar.datasources.label=grafana_datasource
```

Port-forward Grafana :

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3001:80
```

> Grafana accessible sur http://localhost:3001 (admin/admin)

## 6. Installation Loki

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

Creer le fichier `single-binary-values.yaml` :

```yaml
loki:
  commonConfig:
    replication_factor: 1
  storage:
    type: filesystem
  schemaConfig:
    configs:
      - from: "2024-01-01"
        store: tsdb
        object_store: filesystem
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
singleBinary:
  replicas: 1
gateway:
  enabled: true
read:
  replicas: 0
write:
  replicas: 0
backend:
  replicas: 0
monitoring:
  lokiCanary:
    enabled: false
  selfMonitoring:
    enabled: false
    grafanaAgent:
      installOperator: false
test:
  enabled: false
```

> **Fix applique** : Utiliser `single-binary-values.yaml` avec `gateway.enabled=true`. L'URL Loki correcte est `http://loki-gateway.monitoring.svc.cluster.local` (pas `http://loki.monitoring.svc.cluster.local:3100`).

```bash
helm install loki grafana/loki \
  --namespace monitoring \
  -f single-binary-values.yaml
```

## 7. Installation Promtail

```bash
helm install promtail grafana/promtail \
  --namespace monitoring \
  --set "config.clients[0].url=http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push"
```

## 8. Configuration du ConfigMap Loki datasource

```bash
kubectl apply -f monitoring/loki-datasource.yaml
```

> **Fix applique** : Le ConfigMap doit avoir le label `grafana_datasource: "1"` et `app.kubernetes.io/part-of: kube-prometheus-stack` pour etre auto-detecte par le sidecar Grafana.

## 9. Deploiement des Helm charts

```bash
kubectl create namespace production

helm install backend helm/backend --namespace production
helm install frontend helm/frontend --namespace production
```

Verifier le deploiement :

```bash
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production
```

## 10. Application des apps ArgoCD

```bash
kubectl apply -f helm/argocd/backend-app.yaml
kubectl apply -f helm/argocd/frontend-app.yaml
```

Verifier la synchronisation :

```bash
kubectl get applications -n argocd
```

## Corrections et fix importants appliques

| Probleme | Fix |
|---|---|
| Minikube OOM avec la stack complete | `--memory=10240` |
| GitHub Actions runners = AMD64 | `platforms: linux/amd64` pour build/test/scan |
| Images multi-arch pour GHCR | `platforms: linux/amd64,linux/arm64` + QEMU dans le job push |
| Dockerfiles hardcodes ARM64 | Retrait de `--platform=linux/arm64`, plateforme geree par Buildx |
| Alpine + QEMU = problemes | Images Debian slim (`node:22-slim`, `nginx:1.27`) au lieu d'Alpine pour le frontend |
| `apt-get upgrade` dans les Dockerfiles | Mise a jour de libcrypto3, libssl3, libxml2 |
| Django `TestCase` sans DB | Utiliser `SimpleTestCase` (pas de base de donnees configuree) |
| `tsc` compile les fichiers test | Ajouter `exclude` dans `tsconfig.json` pour `*.test.tsx` |
| Vitest pas Jest | `npm test` sans `--watchAll=false` (Vitest detecte le CI automatiquement) |
| URL Loki incorrecte | `http://loki-gateway.monitoring.svc.cluster.local` (pas port 3100) |
| SonarQube monitoringPasscode | Requis dans les secrets Vault |
| SonarQube community edition | `community.enabled=true` si deploye en local |
| Loki mode single-binary | Utiliser `single-binary-values.yaml` avec gateway |
| ConfigMap Loki non detecte | Labels `grafana_datasource=1` + `app.kubernetes.io/part-of=kube-prometheus-stack` |
| Django trailing slash | URLs avec `/` final (`api/hello/`, `health/`) |
| Django CVE-2025-64459 | Mise a jour vers Django 5.1.14 |
