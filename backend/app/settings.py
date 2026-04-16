import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-prod")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "screening",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "app.urls"

WSGI_APPLICATION = "app.wsgi.application"

DB_HOST = os.environ.get("DB_HOST", "")

if DB_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "autism_screening"),
            "USER": os.environ.get("DB_USER", "django"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "django"),
            "HOST": DB_HOST,
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Autism Pre-Screening Platform API",
    "DESCRIPTION": (
        "API de pre-depistage des Troubles du Spectre Autistique (TSA) chez l'enfant.\n\n"
        "**AVERTISSEMENT** : Ce systeme n'est PAS un outil de diagnostic. "
        "Il fournit uniquement une estimation du risque et une recommandation de consultation."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "Sessions", "description": "Gestion des sessions de depistage"},
        {"name": "Questionnaire", "description": "Questions adaptees par age"},
        {"name": "Answers", "description": "Soumission des reponses"},
        {"name": "Analysis", "description": "Analyse et resultats"},
        {"name": "Providers", "description": "Professionnels de sante"},
        {"name": "Health", "description": "Health check"},
    ],
}

# Anthropic API (Claude) for AI summary layer
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Provider matching default radius in km
PROVIDER_SEARCH_RADIUS_KM = int(os.environ.get("PROVIDER_SEARCH_RADIUS_KM", "30"))
