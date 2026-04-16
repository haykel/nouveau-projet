# CLAUDE.md - Autism Pre-Screening Platform

## Projet

Plateforme medicale de pre-depistage des Troubles du Spectre Autistique (TSA) chez l'enfant. Systeme d'estimation du risque avec approche hybride : moteur de regles cliniques + couche d'interpretation IA + couche de securite medicale.

**AVERTISSEMENT FONDAMENTAL** : Ce systeme n'est PAS un outil de diagnostic. Il ne doit JAMAIS produire de diagnostic definitif. Il fournit uniquement une estimation du risque, une detection de signaux d'alerte, et une recommandation de consultation.

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Django 5.1 + Django REST Framework |
| Base de donnees | PostgreSQL 16 (SQLite en dev local) |
| ORM | Django ORM |
| API | REST |
| IA | Claude API (Anthropic SDK) |
| WSGI | Gunicorn |
| Tests | Django TestCase / SimpleTestCase |
| Conteneurisation | Docker (multi-stage) |
| Orchestration | Kubernetes (Minikube) |
| CI/CD | GitHub Actions |
| GitOps | ArgoCD |
| Secrets | HashiCorp Vault |
| Monitoring | Prometheus + Grafana + Loki |

## Architecture modulaire

Le backend est organise en une app Django `screening` avec des services independants :

| Service | Fichier | Responsabilite |
|---|---|---|
| Views (Session/Answer) | `screening/views.py` | Creation sessions, collecte reponses, declenchement analyse |
| `RuleEngineService` | `screening/services/rule_engine.py` | Scoring clinique, detection des red flags, seuils de recommandation |
| `AISummaryService` | `screening/services/ai_summary.py` | Resume narratif structure via Claude API |
| `SafetyValidationService` | `screening/services/safety_validation.py` | Validation post-traitement, blocage du langage diagnostique |
| `ProviderMatcherService` | `screening/services/provider_matcher.py` | Matching geographique (haversine) de professionnels de sante |
| `ResultComposerService` | `screening/services/result_composer.py` | Orchestration des 3 couches et assemblage du resultat final |

## Modele de decision hybride (3 couches)

### Couche 1 : Moteur de regles cliniques (PRIMAIRE)

Le moteur de regles est la source principale de decision. Il effectue :
- Filtrage des questions par tranche d'age (`QuestionBlock`)
- Scoring par reponse (poids configurable via `score_weight`)
- Scoring par domaine (communication, interaction sociale, comportements, sensoriel)
- Detection des signaux critiques via `trigger_flag` + `is_red_flag` sur les options
- Seuils : `HIGH_THRESHOLD = 0.65`, `MEDIUM_THRESHOLD = 0.40`
- Niveaux de recommandation :
  - `monitor` : surveillance, pas de risque significatif
  - `pediatric_consultation` : score >= seuil moyen
  - `specialist_consultation` : score >= seuil eleve
  - `urgent_referral` : regression langagiere/sociale/perte de competences

### Couche 2 : Interpretation IA (SUPPORT)

L'IA recoit uniquement des donnees structurees et produit un resume en francais.
Fallback automatique si `ANTHROPIC_API_KEY` non configure.

L'IA ne doit JAMAIS :
- Diagnostiquer le TSA
- Surcharger les red flags du moteur de regles
- Remplacer les regles de seuil
- Exprimer une certitude medicale

### Couche 3 : Garde-fous de securite (VALIDATION)

Module de post-traitement (`SafetyValidationService`) qui :
- Scanne tout texte genere avec des regex (FR + EN)
- Bloque le langage diagnostique
- Ajoute automatiquement le disclaimer obligatoire
- Remplace le texte entier si des violations sont detectees

Formulations INTERDITES :
- "L'enfant a l'autisme" / "has autism"
- "Cela confirme l'autisme" / "confirms autism"
- "L'enfant n'a pas l'autisme" / "does not have autism"
- Tout enonce de type diagnostique ou de certitude medicale

## Schema de base de donnees

8 tables Django ORM definies dans `screening/models.py` :
- `screening_sessions` : session de depistage (UUID pk, parent, enfant, age, geolocalisation)
- `questions` : banque de questions avec domaine, poids, tranche d'age, type, trigger_flag
- `question_options` : options de reponse avec score et indicateur is_red_flag
- `question_blocks` : blocs de questions groupes par age
- `block_questions` : association M2M bloc-question avec ordre
- `answers` : reponses collectees avec score calcule (unique par session+question)
- `analysis_results` : resultats d'analyse (OneToOne avec session)
- `providers` : professionnels de sante avec geolocalisation

## Endpoints API

| Methode | Route | Description |
|---|---|---|
| `POST` | `/api/sessions/` | Creer une session de depistage |
| `GET` | `/api/sessions/<uuid>/` | Recuperer une session |
| `GET` | `/api/sessions/<uuid>/questions/` | Questions adaptees a l'age |
| `POST` | `/api/sessions/<uuid>/answers/` | Soumettre les reponses |
| `POST` | `/api/sessions/<uuid>/analyze/` | Lancer l'analyse complete |
| `GET` | `/api/sessions/<uuid>/results/` | Recuperer les resultats |
| `GET` | `/api/providers/nearby/?lat=X&lng=Y` | Professionnels proches |
| `GET` | `/health/` | Health check |

## Commandes de developpement

```bash
# Installation
pip install -r requirements.txt

# Migrations
python manage.py makemigrations
python manage.py migrate

# Charger les donnees de seed (questions, blocs, providers)
python manage.py seed_questions

# Demarrage en dev
python manage.py runserver

# Tests
python manage.py test

# Docker Compose (dev local)
docker-compose up --build
# Backend  : http://localhost:8000
# Postgres : localhost:5432
```

## Deploiement Kubernetes

```bash
# Demarrage Minikube (Apple Silicon M4)
minikube start --driver=docker --cpus=4 --memory=10240 --kubernetes-version=v1.31.0
minikube addons enable ingress

# Namespaces
kubectl create namespace argocd
kubectl create namespace vault
kubectl create namespace monitoring
kubectl create namespace production

# ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault --namespace vault \
  --set "server.dev.enabled=true" --set "server.dev.devRootToken=root"

# Secrets Vault
kubectl exec -n vault vault-0 -- vault kv put secret/autism-screening \
  DJANGO_SECRET_KEY="your-production-secret-key" \
  ANTHROPIC_API_KEY="your-api-key" \
  DB_PASSWORD="your-db-password"

# Monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin \
  --set grafana.sidecar.datasources.enabled=true

# Deploiement applicatif
helm install backend helm/backend --namespace production
```

## Regles de developpement

- Ne JAMAIS generer de sortie diagnostique definitive
- Le moteur de regles a toujours la priorite sur l'IA
- Toute sortie texte doit passer par le `SafetyValidationService`
- Les red flags ne peuvent pas etre surcharges par l'IA
- Les donnees de sante doivent etre chiffrees
- Les tests doivent couvrir les scenarios de securite medicale
- Utiliser `SimpleTestCase` quand pas de base de donnees requise
- URLs Django avec `/` final (trailing slash)

## Conventions

- Code en anglais, commentaires en anglais
- Noms de variables et fonctions en snake_case (Python/Django)
- Noms de tables en snake_case (PostgreSQL)
- API RESTful avec codes HTTP standards
- Validation des entrees avec DRF serializers
- Gestion d'erreurs via DRF exception handling
