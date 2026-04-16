import requests as http_requests

from django.contrib import admin, messages
from unfold.admin import ModelAdmin

from .models import DataSource


@admin.register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = [
        "name",
        "is_active",
        "priority",
        "is_healthy",
        "requests_today",
        "rate_limit_per_day",
        "consecutive_errors",
        "updated_at",
    ]
    list_filter = ["is_active", "is_healthy", "priority"]
    search_fields = ["name"]
    readonly_fields = [
        "requests_today",
        "last_reset",
        "is_healthy",
        "consecutive_errors",
        "created_at",
        "updated_at",
    ]
    actions = [
        "activate_sources",
        "deactivate_sources",
        "reset_counters",
        "test_connectivity",
    ]

    fieldsets = (
        (None, {"fields": ("name", "priority", "is_active")}),
        ("API", {"fields": ("_api_key", "base_url")}),
        (
            "Limites",
            {"fields": ("rate_limit_per_minute", "rate_limit_per_day")},
        ),
        (
            "État",
            {
                "fields": (
                    "is_healthy",
                    "consecutive_errors",
                    "requests_today",
                    "last_reset",
                )
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )

    @admin.action(description="Activer les sources sélectionnées")
    def activate_sources(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} source(s) activée(s).")

    @admin.action(description="Désactiver les sources sélectionnées")
    def deactivate_sources(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} source(s) désactivée(s).")

    @admin.action(description="Réinitialiser les compteurs de requêtes")
    def reset_counters(self, request, queryset):
        for source in queryset:
            source.reset_counter()
        self.message_user(request, f"{queryset.count()} compteur(s) réinitialisé(s).")

    @admin.action(description="Tester la connectivité")
    def test_connectivity(self, request, queryset):
        for source in queryset:
            try:
                _ping_source(source)
                source.mark_healthy()
                self.message_user(
                    request,
                    f"{source.name} : connectivité OK",
                    messages.SUCCESS,
                )
            except Exception as e:
                source.record_error()
                self.message_user(
                    request,
                    f"{source.name} : échec — {e}",
                    messages.ERROR,
                )


def _ping_source(source: DataSource):
    name = source.name.lower()
    api_key = source.api_key

    if "finnhub" in name:
        url = f"{source.base_url or 'https://finnhub.io'}/api/v1/quote"
        resp = http_requests.get(url, params={"symbol": "AAPL", "token": api_key}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("c", 0) == 0:
            raise ValueError("Réponse vide de Finnhub")

    elif "alpha" in name or "vantage" in name:
        url = f"{source.base_url or 'https://www.alphavantage.co'}/query"
        resp = http_requests.get(
            url,
            params={"function": "GLOBAL_QUOTE", "symbol": "AAPL", "apikey": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if "Global Quote" not in data:
            raise ValueError("Réponse invalide d'Alpha Vantage")

    else:
        base = source.base_url
        if not base:
            raise ValueError(f"Pas de base_url configurée pour {source.name}")
        resp = http_requests.get(base, timeout=10)
        resp.raise_for_status()
