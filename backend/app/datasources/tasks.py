import requests as http_requests

from celery import shared_task
from django.utils import timezone

from .models import DataSource


@shared_task
def reset_daily_counters():
    updated = DataSource.objects.filter(is_active=True).update(
        requests_today=0,
        last_reset=timezone.now(),
    )
    return f"{updated} compteur(s) réinitialisé(s)"


@shared_task
def check_sources_health():
    sources = DataSource.objects.filter(is_active=True)
    results = []

    for source in sources:
        try:
            name = source.name.lower()
            api_key = source.api_key

            if "finnhub" in name:
                url = f"{source.base_url or 'https://finnhub.io'}/api/v1/quote"
                resp = http_requests.get(
                    url, params={"symbol": "AAPL", "token": api_key}, timeout=10
                )
                resp.raise_for_status()

            elif "alpha" in name or "vantage" in name:
                url = f"{source.base_url or 'https://www.alphavantage.co'}/query"
                resp = http_requests.get(
                    url,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": "AAPL",
                        "apikey": api_key,
                    },
                    timeout=10,
                )
                resp.raise_for_status()

            source.mark_healthy()
            results.append(f"{source.name}: OK")

        except Exception as e:
            source.record_error()
            results.append(f"{source.name}: ERREUR — {e}")

    return results


@shared_task
def update_top10():
    from .router import DataSourceRouter
    from .services import get_datasource_service

    router = DataSourceRouter()
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "WMT"]
    results = []

    for ticker in tickers:
        try:
            def fetch(source, t=ticker):
                svc = get_datasource_service(source)
                return svc.get_quote(t)

            router.execute_with_fallback(fetch)
            results.append(f"{ticker}: OK")
        except Exception as e:
            results.append(f"{ticker}: ERREUR — {e}")

    return results
