# Autism Pre-Screening Platform

Plateforme medicale de pre-depistage des Troubles du Spectre Autistique (TSA) chez l'enfant, avec une approche hybride combinant un moteur de regles cliniques, une couche d'interpretation IA, et des garde-fous de securite medicale.

> **Ce systeme n'est PAS un outil de diagnostic.** Il fournit une estimation du risque, une detection de signaux d'alerte, et une recommandation de consultation professionnelle.

## Architecture

```
                         Intake
                           |
                    +------v------+
                    |   Session   |
                    |   (views)   |
                    +------+------+
                           |
                    +------v------+
                    | Questionnaire|
                    |  (age-based |
                    |   blocks)   |
                    +------+------+
                           |
                    +------v------+
                    |   Answers   |
                    |   (views)   |
                    +------+------+
                           |
              +------------+------------+
              |                         |
       +------v------+          +------v------+
       | Rule Engine  |          |     AI      |
       | (scoring,    |          | Summary     |
       |  red flags,  |          | (Claude API)|
       |  thresholds) |          |             |
       +------+------+          +------+------+
              |                         |
              +------------+------------+
                           |
                    +------v------+
                    |   Safety    |
                    | Validation  |
                    +------+------+
                           |
              +------------+------------+
              |                         |
       +------v------+          +------v------+
       |   Result    |          |  Provider   |
       |  Composer   |          |  Matcher    |
       +-------------+          +-------------+
```

## Modele de decision hybride

| Couche | Role | Priorite |
|---|---|---|
| Moteur de regles cliniques | Scoring, red flags, seuils, recommandation | **Primaire** |
| Interpretation IA (Claude) | Resume narratif, explications, formulation | Support |
| Garde-fous de securite | Validation du langage, blocage diagnostique | Obligatoire |

### Niveaux de recommandation

| Niveau | Condition |
|---|---|
| `monitor` | Score faible, pas de signaux critiques |
| `pediatric_consultation` | Score >= seuil moyen (40%) |
| `specialist_consultation` | Score >= seuil eleve (65%) |
| `urgent_referral` | Regression langagiere ou sociale detectee |

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Django 5.1 + Django REST Framework |
| Base de donnees | PostgreSQL 16 |
| ORM | Django ORM |
| IA | Claude API (Anthropic SDK) |
| WSGI | Gunicorn |
| Conteneurisation | Docker (multi-stage, multi-arch) |
| Orchestration | Kubernetes (Minikube) |
| CI/CD | GitHub Actions |
| GitOps | ArgoCD |
| Secrets | HashiCorp Vault |
| Monitoring | Prometheus + Grafana + Loki |

## Structure du projet

```
autism-screening-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py               # health endpoint
│   │   └── wsgi.py
│   ├── screening/
│   │   ├── models.py              # 8 models (Session, Question, Answer, etc.)
│   │   ├── serializers.py         # DRF serializers
│   │   ├── views.py               # API views
│   │   ├── urls.py                # URL routing
│   │   ├── admin.py               # Django admin config
│   │   ├── tests.py               # Tests unitaires
│   │   ├── services/
│   │   │   ├── rule_engine.py     # Scoring, red flags, thresholds
│   │   │   ├── ai_summary.py      # Claude API integration
│   │   │   ├── safety_validation.py # Post-processing safety
│   │   │   ├── provider_matcher.py  # Geolocation matching
│   │   │   └── result_composer.py   # Orchestration
│   │   └── management/
│   │       └── commands/
│   │           └── seed_questions.py # Seed data
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── helm/
│   ├── backend/
│   └── argocd/
├── infrastructure/
│   └── postgresql/
├── monitoring/
│   └── loki-datasource.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

## Prerequis

- Python 3.12+
- PostgreSQL 16 (ou Docker)
- macOS avec Apple Silicon (M1/M2/M3/M4) pour le deploiement K8s
- Docker Desktop

## Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/haykel/autism-screening-platform.git
cd autism-screening-platform

# 2. Installer les dependances
cd backend
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py migrate

# 4. Charger les donnees de seed
python manage.py seed_questions

# 5. Lancer le serveur
python manage.py runserver
# Backend : http://localhost:8000

# Ou avec Docker Compose
docker-compose up --build
# Backend  : http://localhost:8000
# Postgres : localhost:5432
```

## Variables d'environnement

| Variable | Description | Defaut |
|---|---|---|
| `DJANGO_SECRET_KEY` | Cle secrete Django | `dev-secret-key-change-in-prod` |
| `DJANGO_DEBUG` | Mode debug | `False` |
| `DB_HOST` | Host PostgreSQL (vide = SQLite) | `` |
| `DB_NAME` | Nom de la base | `autism_screening` |
| `DB_USER` | Utilisateur PostgreSQL | `django` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `django` |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `ANTHROPIC_API_KEY` | Cle API Claude (optionnelle) | `` |
| `PROVIDER_SEARCH_RADIUS_KM` | Rayon de recherche providers | `30` |

## API Endpoints

### Session

```
POST   /api/sessions/                     Creer une session de depistage
GET    /api/sessions/<uuid>/              Recuperer une session
```

### Questionnaire

```
GET    /api/sessions/<uuid>/questions/    Questions adaptees a l'age de l'enfant
```

### Reponses

```
POST   /api/sessions/<uuid>/answers/      Soumettre les reponses
```

### Analyse

```
POST   /api/sessions/<uuid>/analyze/      Lancer l'analyse complete (3 couches)
GET    /api/sessions/<uuid>/results/      Recuperer les resultats
```

### Professionnels

```
GET    /api/providers/nearby/?lat=X&lng=Y&radius=Z    Professionnels proches
```

### Health

```
GET    /health/                           Health check
```

### Exemple de flux complet

**1. Creation de session**

```json
POST /api/sessions/
{
  "parent_name": "Marie Dupont",
  "child_first_name": "Lucas",
  "child_age_months": 24,
  "child_sex": "M",
  "respondent_role": "mother",
  "main_concerns": ["ne parle pas encore", "ne repond pas a son prenom"],
  "address": "15 rue de la Paix",
  "postal_code": "75002",
  "city": "Paris",
  "lat": 48.8698,
  "lng": 2.3311
}
```

**2. Soumission des reponses**

```json
POST /api/sessions/<uuid>/answers/
{
  "answers": [
    { "question_id": 1, "selected_option_id": 4, "raw_value": "never" },
    { "question_id": 2, "selected_option_id": 8, "raw_value": "never" }
  ]
}
```

**3. Resultat d'analyse**

```json
GET /api/sessions/<uuid>/results/
{
  "global_score": 28.0,
  "risk_level": "high",
  "recommendation_level": "specialist_consultation",
  "red_flags": ["no_response_to_name", "no_single_words_at_24_months"],
  "domain_scores": {
    "communication": { "score": 12.0, "max_score": 18.0, "percentage": 66.7 },
    "social_interaction": { "score": 9.0, "max_score": 15.0, "percentage": 60.0 }
  },
  "ai_summary": "Les reponses indiquent des preoccupations notables...",
  "explanation_json": {
    "summary": "Ce depistage suggere un niveau de preoccupation eleve.",
    "details": "Des indicateurs dans les domaines communication, social_interaction...",
    "nextSteps": "Nous recommandons de consulter un specialiste...",
    "disclaimer": "Ce resultat ne constitue pas un diagnostic..."
  },
  "nearby_providers": [
    {
      "name": "Dr. Sophie Martin",
      "specialty": "Neuropediatre",
      "address": "25 boulevard Haussmann, 75009 Paris",
      "phone": "01 42 00 00 01",
      "distance_km": 1.2
    }
  ]
}
```

## Tests

```bash
# Tous les tests
python manage.py test

# Tests de l'app screening uniquement
python manage.py test screening

# Tests avec verbosity
python manage.py test screening --verbosity=2
```

## Deploiement

Pour le deploiement Kubernetes complet sur Minikube (Apple Silicon M4), voir [CLAUDE.md](CLAUDE.md).

## Securite et conformite

- Chiffrement des donnees au repos et en transit
- Controle d'acces
- Journalisation d'audit
- Retention minimale des donnees
- Conformite RGPD

## Licence

Projet prive - Usage medical reserve.
