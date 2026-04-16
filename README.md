# mon-projet-devops

Projet fullstack React + Django avec pipeline CI/CD, deploiement Kubernetes via Helm/ArgoCD, et monitoring complet (Prometheus, Grafana, Loki).

Optimise pour Apple Silicon M4 (ARM64).

## Architecture

```
                    ┌─────────────┐
                    │  GitHub      │
                    │  Actions     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         Build/Test    SonarQube    Trivy Scan
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │    GHCR     │
                    │  (images)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   ArgoCD    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────┐
       │  Frontend    │          │  Backend     │
       │  React/Nginx │          │  Django/DRF  │
       │  :80         │          │  :8000       │
       └─────────────┘          └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Monitoring  │
                    │  Prometheus  │
                    │  Grafana     │
                    │  Loki        │
                    └─────────────┘
```

## Prerequis

- macOS avec Apple Silicon (M1/M2/M3/M4)
- Docker Desktop
- Homebrew

```bash
brew install minikube kubectl helm vault trivy
```

## Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/haykel/mon-projet-devops.git
cd mon-projet-devops

# 2. Lancer en local avec Docker Compose
docker-compose up --build

# Frontend : http://localhost:3000
# Backend  : http://localhost:8000/api/hello/
# Health   : http://localhost:8000/health/
```

Pour le deploiement Kubernetes complet, voir [CLAUDE.md](CLAUDE.md).

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Frontend | React + TypeScript + Vite | React 19, Vite 6 |
| Backend | Django + Django REST Framework | Django 5.1.14, DRF 3.15 |
| Serveur web | Nginx | 1.27 |
| WSGI | Gunicorn | 23.0 |
| Container | Docker (multi-stage, multi-arch) | - |
| Orchestration | Kubernetes (Minikube) | 1.31 |
| CI/CD | GitHub Actions | - |
| GitOps | ArgoCD | - |
| Registry | GitHub Container Registry (ghcr.io) | - |
| Qualite | SonarCloud | - |
| Securite | Trivy | - |
| Secrets | HashiCorp Vault | - |
| Monitoring | Prometheus + Grafana | kube-prometheus-stack |
| Logs | Loki + Promtail | - |

## Structure du projet

```
mon-projet-devops/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── settings.py          # Django config (DRF, no DB)
│   │   ├── urls.py              # /api/hello/, /health/
│   │   ├── views.py             # Endpoints DRF
│   │   ├── tests.py             # SimpleTestCase
│   │   └── wsgi.py
│   ├── Dockerfile               # python:3.12-slim-bookworm, multi-stage (base/test/production)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Hello World
│   │   ├── App.test.tsx         # Test Vitest
│   │   ├── main.tsx
│   │   └── setupTests.ts
│   ├── Dockerfile               # node:22-slim build + nginx:1.27 production
│   ├── index.html
│   ├── nginx.conf               # SPA + proxy /api/ -> backend
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── helm/
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml          # 2 replicas, healthcheck /health
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── ingress.yaml     # app.local/api
│   ├── frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml          # 2 replicas
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── ingress.yaml     # app.local/
│   └── argocd/
│       ├── backend-app.yaml     # Auto-sync, prune, selfHeal
│       └── frontend-app.yaml
├── monitoring/
│   └── loki-datasource.yaml     # ConfigMap Grafana datasource
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # 4 jobs pipeline
├── docker-compose.yml
├── .gitignore
├── CLAUDE.md                    # Instructions d'installation DevOps
└── README.md
```

## Pipeline CI/CD

Declenche sur push et pull request vers `main`.

```
push/PR -> main
       |
       v
┌─────────────────┐
│  Build & Test    │  Build images (amd64), tests Django + Vitest
└───────┬─────────┘
        |
   ┌────┴────┐
   v         v
┌────────┐ ┌──────────┐
│Sonar   │ │ Trivy    │  Qualite code + scan CVE critiques
│Cloud   │ │ Security │
└───┬────┘ └────┬─────┘
    |           |
    └─────┬─────┘
          v
   ┌─────────────┐
   │ Push GHCR   │  Images multi-arch (amd64 + arm64)
   └─────────────┘
```

### Images Docker

```
ghcr.io/haykel/mon-projet-devops/frontend:latest
ghcr.io/haykel/mon-projet-devops/frontend:<sha>
ghcr.io/haykel/mon-projet-devops/backend:latest
ghcr.io/haykel/mon-projet-devops/backend:<sha>
```

### Secrets GitHub requis

| Secret | Description |
|---|---|
| `GITHUB_TOKEN` | Automatique, pour push GHCR |
| `SONAR_TOKEN` | Token SonarCloud |
| `SONAR_HOST_URL` | URL SonarCloud |

## Monitoring

### Acces

| Service | Commande | URL |
|---|---|---|
| Grafana | `kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3001:80` | http://localhost:3001 |
| Prometheus | `kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090` | http://localhost:9090 |
| ArgoCD | `kubectl port-forward svc/argocd-server -n argocd 8080:443` | https://localhost:8080 |

### Datasources Grafana

- **Prometheus** : auto-configure par kube-prometheus-stack
- **Loki** : auto-configure via ConfigMap avec label `grafana_datasource=1`

## Commandes utiles

```bash
# Docker Compose (dev local)
docker-compose up --build          # Lancer le projet
docker-compose down                # Arreter

# Tests
docker build --target test ./backend    # Tests Django dans le build
cd frontend && npm test                 # Tests Vitest

# Kubernetes
kubectl get pods -n production          # Pods applicatifs
kubectl get pods -n monitoring          # Pods monitoring
kubectl get pods -n argocd              # Pods ArgoCD
kubectl get ingress -n production       # Ingress rules

# Helm
helm install backend helm/backend -n production --create-namespace
helm install frontend helm/frontend -n production
helm upgrade backend helm/backend -n production
helm list -n production

# ArgoCD
kubectl get applications -n argocd      # Etat des apps
kubectl apply -f helm/argocd/           # Deployer les apps

# Logs
kubectl logs -l app=backend -n production
kubectl logs -l app=frontend -n production
```

## Troubleshooting

### Minikube OOM / pods en CrashLoopBackOff

```bash
minikube start --memory=10240
```

La stack complete (ArgoCD + Vault + Prometheus + Grafana + Loki) necessite au minimum 10 Go de RAM.

### Build Docker echoue sur GitHub Actions

Les runners GitHub sont AMD64. Les Dockerfiles ne doivent pas contenir `--platform=linux/arm64`. La plateforme est geree par `docker/build-push-action` avec le parametre `platforms`.

### QEMU + Alpine = segfault

Utiliser des images Debian slim (`node:22-slim`, `nginx:1.27`) au lieu d'Alpine pour les builds multi-arch avec QEMU.

### Tests Django : ImproperlyConfigured DATABASES

Utiliser `SimpleTestCase` au lieu de `TestCase` quand il n'y a pas de base de donnees configuree.

### tsc compile les fichiers test

Ajouter dans `tsconfig.json` :

```json
"exclude": ["src/**/*.test.tsx", "src/**/*.test.ts", "src/setupTests.ts"]
```

### Loki datasource non visible dans Grafana

Verifier les labels du ConfigMap :

```yaml
labels:
  grafana_datasource: "1"
  app.kubernetes.io/part-of: kube-prometheus-stack
```

### URL Loki incorrecte

Avec le mode single-binary + gateway, l'URL est :

```
http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push
```

Et non `http://loki:3100`.
