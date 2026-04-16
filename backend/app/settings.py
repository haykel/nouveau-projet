import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-prod")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

FIXTURE_DIRS = [
    BASE_DIR / "fixtures",
]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "app.datasources",
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

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "app.urls"

DB_HOST = os.environ.get("DB_HOST", "")

if DB_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "investissement"),
            "USER": os.environ.get("DB_USER", "django"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "Django2026!"),
            "HOST": DB_HOST,
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get(
            "REDIS_URL", "redis://:Redis2026!@redis:6379/0"
        ),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery
CELERY_BROKER_URL = os.environ.get(
    "REDIS_URL", "redis://:Redis2026!@redis:6379/0"
)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Paris"
CELERY_BEAT_SCHEDULE = {
    "reset-daily-counters": {
        "task": "app.datasources.tasks.reset_daily_counters",
        "schedule": 86400,  # every 24h
    },
    "check-sources-health": {
        "task": "app.datasources.tasks.check_sources_health",
        "schedule": 300,  # every 5 minutes
    },
    "update-top10": {
        "task": "app.datasources.tasks.update_top10",
        "schedule": 900,  # every 15 minutes
    },
}

# Finnhub
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")

# Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")

# Keycloak
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "investissement")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "backend")

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "app.authentication.KeycloakAuthentication",
    ],
    "UNAUTHENTICATED_USER": None,
}

# Unfold Admin Theme
UNFOLD = {
    "SITE_TITLE": "Plateforme Investissement",
    "SITE_HEADER": "Administration",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
}
