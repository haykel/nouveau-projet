import json

from django.core.cache import cache
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from app.authentication import KeycloakAuthentication, require_role
from app.stocks.services import FinnhubService, FinnhubServiceError
from app.stocks.indicators import TechnicalIndicators


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def search_stocks(request):
    """GET /api/stocks/search/?q=AAPL"""
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response(
            {"error": "Query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        service = FinnhubService()
        results = service.search_symbol(query)
        return Response({"results": results})
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_detail(request, ticker):
    """GET /api/stocks/{ticker}/"""
    try:
        service = FinnhubService()
        quote = service.get_quote(ticker)
        return Response(quote)
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_history(request, ticker):
    """GET /api/stocks/{ticker}/history/?period=1m"""
    period = request.query_params.get("period", "1m")

    try:
        service = FinnhubService()
        candles = service.get_candles(ticker, period)
        return Response(candles)
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def market_indices(request):
    """GET /api/markets/indices/"""
    try:
        service = FinnhubService()
        indices = service.get_market_indices()
        return Response({"indices": indices})
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


def _get_candle_data(ticker: str, period: str = "3m") -> dict:
    cache_key = f"candles:{ticker.upper()}:{period}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    service = FinnhubService()
    data = service.get_candles(ticker, period)
    cache.set(cache_key, json.dumps(data), timeout=300)
    return data


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_indicators(request, ticker):
    """GET /api/stocks/{ticker}/indicators/?indicators=rsi,macd,ma20,ma50,bb&period=3m"""
    requested = request.query_params.get("indicators", "rsi,macd,ma20,ma50,bb")
    period = request.query_params.get("period", "3m")
    indicator_list = [i.strip().lower() for i in requested.split(",")]

    cache_key = f"indicators:{ticker.upper()}:{period}:{requested}"
    cached = cache.get(cache_key)
    if cached:
        return Response(json.loads(cached))

    try:
        data = _get_candle_data(ticker, period)
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    candles = data.get("candles", [])
    if not candles:
        return Response({"error": "Pas de données disponibles"}, status=status.HTTP_404_NOT_FOUND)

    times = [c.get("time") or c.get("timestamp") for c in candles]
    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]

    result: dict = {"symbol": ticker.upper(), "timestamps": times}

    if "rsi" in indicator_list:
        result["rsi"] = TechnicalIndicators.calculate_rsi(closes)

    if "macd" in indicator_list:
        result["macd"] = TechnicalIndicators.calculate_macd(closes)

    if "ma20" in indicator_list:
        result["ma20"] = TechnicalIndicators.calculate_ma(closes, 20)

    if "ma50" in indicator_list:
        result["ma50"] = TechnicalIndicators.calculate_ma(closes, 50)

    if "ema20" in indicator_list:
        result["ema20"] = TechnicalIndicators.calculate_ema(closes, 20)

    if "ema50" in indicator_list:
        result["ema50"] = TechnicalIndicators.calculate_ema(closes, 50)

    if "bb" in indicator_list:
        result["bollinger"] = TechnicalIndicators.calculate_bollinger_bands(closes)

    if "volume_profile" in indicator_list:
        result["volume_profile"] = TechnicalIndicators.calculate_volume_profile(closes, volumes)

    cache.set(cache_key, json.dumps(result), timeout=300)
    return Response(result)


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_score(request, ticker):
    """GET /api/stocks/{ticker}/score/"""
    cache_key = f"score:{ticker.upper()}"
    cached = cache.get(cache_key)
    if cached:
        return Response(json.loads(cached))

    try:
        data = _get_candle_data(ticker, "3m")
    except FinnhubServiceError as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    candles = data.get("candles", [])
    if not candles:
        return Response({"error": "Pas de données disponibles"}, status=status.HTTP_404_NOT_FOUND)

    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]

    score_data = TechnicalIndicators.calculate_score(closes, volumes)
    score_data["symbol"] = ticker.upper()

    cache.set(cache_key, json.dumps(score_data), timeout=300)
    return Response(score_data)


TOP_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA",
    "META", "NFLX", "AMD", "INTC", "CRM", "ORCL", "ADBE", "PYPL",
    "JPM", "BAC", "GS", "MS", "V", "MA", "UBER", "LYFT",
    "SPOT", "SNAP", "SQ", "SHOP", "ZM", "DOCU", "COIN", "PLTR",
]


@api_view(["GET"])
@authentication_classes([KeycloakAuthentication])
@require_role("user")
def stock_top10(request):
    """GET /api/stocks/top10/ — Top 10 performers of the day."""
    cache_key = "top10"
    cached = cache.get(cache_key)
    if cached:
        return Response(json.loads(cached))

    service = FinnhubService()
    quotes = []

    for ticker in TOP_TICKERS:
        try:
            quote = service.get_quote(ticker)
            if quote.get("change_percent") is not None:
                quotes.append(quote)
        except FinnhubServiceError:
            continue

    top10 = sorted(quotes, key=lambda q: q.get("change_percent", 0), reverse=True)[:10]
    result = {"top10": top10}

    cache.set(cache_key, json.dumps(result), timeout=900)
    return Response(result)
