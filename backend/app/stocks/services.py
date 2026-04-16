import logging
import time

import finnhub
import requests as http_requests
import yfinance as yf
from django.conf import settings

logger = logging.getLogger(__name__)


YFINANCE_PERIOD_MAP = {
    "1d": ("1d", "5m"),
    "1w": ("5d", "60m"),
    "1m": ("1mo", "1d"),
    "3m": ("3mo", "1d"),
    "1y": ("1y", "1wk"),
    "5y": ("5y", "1mo"),
}

DAILY_INTERVALS = {"1d", "1wk", "1mo"}


def get_history_yfinance(ticker: str, period: str) -> list:
    """Fetch historical OHLCV data from Yahoo Finance using yf.download.

    Returns:
        [{"time": "2026-04-10", "open": 259.98, ...}, ...]
    """
    yf_period, interval = YFINANCE_PERIOD_MAP.get(period, ("1mo", "1d"))

    try:
        df = yf.download(
            ticker.upper(),
            period=yf_period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
    except Exception as e:
        raise FinnhubServiceError(f"Yahoo Finance failed for {ticker}: {e}")

    if df.empty:
        return []

    candles = []
    for date, row in df.iterrows():
        time_str = (
            date.strftime("%Y-%m-%d")
            if interval in DAILY_INTERVALS
            else date.strftime("%Y-%m-%d %H:%M:%S")
        )
        candles.append({
            "time": time_str,
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })

    return candles


class FinnhubServiceError(Exception):
    pass


class FinnhubService:
    """Client wrapper around the Finnhub API with rate-limit handling."""

    # Finnhub free tier: 60 calls/minute
    _last_call_time = 0.0
    _min_interval = 1.0  # seconds between calls

    def __init__(self):
        api_key = settings.FINNHUB_API_KEY
        if not api_key:
            raise FinnhubServiceError("FINNHUB_API_KEY is not configured")
        self.client = finnhub.Client(api_key=api_key)

    def _rate_limit(self):
        """Enforce minimum interval between API calls."""
        now = time.time()
        elapsed = now - FinnhubService._last_call_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        FinnhubService._last_call_time = time.time()

    def get_quote(self, ticker: str) -> dict:
        """Get current price quote for a ticker symbol.

        Returns:
            {
                "symbol": "AAPL",
                "current_price": 150.0,
                "change": 2.5,
                "change_percent": 1.69,
                "high": 151.0,
                "low": 148.0,
                "open": 149.0,
                "previous_close": 147.5,
                "timestamp": 1234567890
            }
        """
        self._rate_limit()
        try:
            data = self.client.quote(ticker.upper())
        except Exception as e:
            raise FinnhubServiceError(f"Failed to fetch quote for {ticker}: {e}")

        if not data or data.get("c", 0) == 0:
            raise FinnhubServiceError(f"No data found for ticker: {ticker}")

        return {
            "symbol": ticker.upper(),
            "current_price": data["c"],
            "change": data["d"],
            "change_percent": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "previous_close": data["pc"],
            "timestamp": data.get("t", 0),
        }

    def search_symbol(self, query: str) -> list:
        """Search for stock symbols matching a query.

        Returns:
            [
                {
                    "symbol": "AAPL",
                    "description": "Apple Inc",
                    "type": "Common Stock"
                },
                ...
            ]
        """
        self._rate_limit()
        try:
            data = self.client.symbol_lookup(query)
        except Exception as e:
            raise FinnhubServiceError(f"Search failed for '{query}': {e}")

        results = data.get("result", [])
        return [
            {
                "symbol": item.get("symbol", ""),
                "description": item.get("description", ""),
                "type": item.get("type", ""),
            }
            for item in results[:20]
        ]

    def get_candles(self, ticker: str, period: str = "1m") -> dict:
        """Get historical candlestick data via Alpha Vantage, with Yahoo Finance fallback.

        Alpha Vantage is the primary source. If it returns a quota/rate-limit
        error ('Information' or 'Note' key), we fall back to Yahoo Finance.

        Args:
            ticker: Stock symbol
            period: Time period - 1d, 1w, 1m, 3m, 1y, 5y

        Returns:
            {
                "symbol": "AAPL",
                "candles": [
                    {"time": "2026-01-15", "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...},
                    ...
                ]
            }
        """
        period_days = {
            "1d": 1,
            "1w": 7,
            "1m": 30,
            "3m": 90,
            "1y": 365,
            "5y": 1825,
        }

        if period not in period_days:
            raise FinnhubServiceError(
                f"Invalid period: {period}. Use: {', '.join(period_days.keys())}"
            )

        # Try Alpha Vantage first
        candles = self._get_history_alphavantage(ticker, period, period_days[period])
        if candles is not None:
            return {"symbol": ticker.upper(), "candles": candles}

        # Fallback to Yahoo Finance
        logger.info("Alpha Vantage quota exceeded, falling back to Yahoo Finance for %s", ticker)
        yf_candles = get_history_yfinance(ticker, period)
        return {"symbol": ticker.upper(), "candles": yf_candles}

    def _get_history_alphavantage(self, ticker: str, period: str, days: int) -> list | None:
        """Fetch from Alpha Vantage. Returns None if quota exceeded (caller should fallback)."""
        api_key = getattr(settings, "ALPHA_VANTAGE_API_KEY", "")
        if not api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not configured, skipping Alpha Vantage")
            return None

        self._rate_limit()
        try:
            resp = http_requests.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "TIME_SERIES_DAILY",
                    "symbol": ticker.upper(),
                    "outputsize": "compact",
                    "apikey": api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("Alpha Vantage request failed for %s: %s", ticker, e)
            return None

        if "Error Message" in data:
            raise FinnhubServiceError(f"No data found for ticker: {ticker}")

        if "Information" in data or "Note" in data:
            logger.warning(
                "Alpha Vantage quota exceeded for %s: %s",
                ticker,
                data.get("Information") or data.get("Note"),
            )
            return None

        ts = data.get("Time Series (Daily)")
        if not ts:
            logger.error(
                "Alpha Vantage response missing 'Time Series (Daily)' for %s. Keys: %s",
                ticker,
                list(data.keys()),
            )
            return None

        sorted_dates = sorted(ts.keys(), reverse=True)[:days]

        candles = []
        for date_str in reversed(sorted_dates):
            entry = ts[date_str]
            candles.append({
                "time": date_str,
                "open": float(entry["1. open"]),
                "high": float(entry["2. high"]),
                "low": float(entry["3. low"]),
                "close": float(entry["4. close"]),
                "volume": int(entry["5. volume"]),
            })

        return candles

    def get_market_indices(self) -> list:
        """Get quotes for major market indices.

        Returns quotes for CAC40, S&P500, NASDAQ, DOW JONES.
        Uses ETFs as proxies since Finnhub free tier doesn't support indices directly.
        """
        indices = [
            {"symbol": "^GSPC", "etf": "SPY", "name": "S&P 500"},
            {"symbol": "^IXIC", "etf": "QQQ", "name": "NASDAQ"},
            {"symbol": "^DJI", "etf": "DIA", "name": "Dow Jones"},
            {"symbol": "^FCHI", "etf": "EWQ", "name": "CAC 40"},
        ]

        results = []
        for index in indices:
            try:
                quote = self.get_quote(index["etf"])
                quote["name"] = index["name"]
                quote["index_symbol"] = index["symbol"]
                quote["symbol"] = index["etf"]
                results.append(quote)
            except FinnhubServiceError:
                results.append(
                    {
                        "name": index["name"],
                        "index_symbol": index["symbol"],
                        "symbol": index["etf"],
                        "current_price": None,
                        "change": None,
                        "change_percent": None,
                        "error": "Data unavailable",
                    }
                )

        return results
