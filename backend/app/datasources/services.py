import time
from abc import ABC, abstractmethod

import finnhub
import requests as http_requests

from .models import DataSource


class BaseDataSource(ABC):
    def __init__(self, source: DataSource):
        self.source = source
        self.api_key = source.api_key

    @abstractmethod
    def get_quote(self, ticker: str) -> dict:
        pass

    @abstractmethod
    def search(self, query: str) -> list:
        pass

    @abstractmethod
    def get_history(self, ticker: str, period: str) -> dict:
        pass


class FinnhubDataSource(BaseDataSource):
    def __init__(self, source: DataSource):
        super().__init__(source)
        self.client = finnhub.Client(api_key=self.api_key)

    def get_quote(self, ticker: str) -> dict:
        data = self.client.quote(ticker.upper())
        if not data or data.get("c", 0) == 0:
            raise ValueError(f"Pas de données pour {ticker}")
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

    def search(self, query: str) -> list:
        data = self.client.symbol_lookup(query)
        return [
            {
                "symbol": item.get("symbol", ""),
                "description": item.get("description", ""),
                "type": item.get("type", ""),
            }
            for item in data.get("result", [])[:20]
        ]

    def get_history(self, ticker: str, period: str = "1m") -> dict:
        now = int(time.time())
        period_map = {
            "1d": (now - 86400, "5"),
            "1w": (now - 604800, "15"),
            "1m": (now - 2592000, "60"),
            "3m": (now - 7776000, "D"),
            "6m": (now - 15552000, "D"),
            "1y": (now - 31536000, "W"),
        }
        if period not in period_map:
            raise ValueError(f"Période invalide : {period}")

        from_ts, resolution = period_map[period]
        data = self.client.stock_candles(ticker.upper(), resolution, from_ts, now)

        if data.get("s") == "no_data":
            return {"symbol": ticker.upper(), "candles": []}

        candles = []
        for i in range(len(data.get("t", []))):
            candles.append({
                "timestamp": data["t"][i],
                "open": data["o"][i],
                "high": data["h"][i],
                "low": data["l"][i],
                "close": data["c"][i],
                "volume": data["v"][i],
            })
        return {"symbol": ticker.upper(), "candles": candles}


class AlphaVantageDataSource(BaseDataSource):
    def __init__(self, source: DataSource):
        super().__init__(source)
        self.base_url = source.base_url or "https://www.alphavantage.co"

    def _request(self, params: dict) -> dict:
        params["apikey"] = self.api_key
        resp = http_requests.get(f"{self.base_url}/query", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "Error Message" in data or "Note" in data:
            raise ValueError(data.get("Error Message") or data.get("Note"))
        return data

    def get_quote(self, ticker: str) -> dict:
        data = self._request({"function": "GLOBAL_QUOTE", "symbol": ticker.upper()})
        gq = data.get("Global Quote", {})
        if not gq:
            raise ValueError(f"Pas de données pour {ticker}")

        price = float(gq.get("05. price", 0))
        change = float(gq.get("09. change", 0))
        change_pct_raw = gq.get("10. change percent", "0%")
        change_pct = float(change_pct_raw.replace("%", ""))

        return {
            "symbol": ticker.upper(),
            "current_price": price,
            "change": change,
            "change_percent": change_pct,
            "high": float(gq.get("03. high", 0)),
            "low": float(gq.get("04. low", 0)),
            "open": float(gq.get("02. open", 0)),
            "previous_close": float(gq.get("08. previous close", 0)),
            "timestamp": 0,
        }

    def search(self, query: str) -> list:
        data = self._request({"function": "SYMBOL_SEARCH", "keywords": query})
        return [
            {
                "symbol": item.get("1. symbol", ""),
                "description": item.get("2. name", ""),
                "type": item.get("3. type", ""),
            }
            for item in data.get("bestMatches", [])[:20]
        ]

    def get_history(self, ticker: str, period: str = "1m") -> dict:
        data = self._request({
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker.upper(),
            "outputsize": "compact" if period in ("1d", "1w", "1m") else "full",
        })

        ts = data.get("Time Series (Daily)", {})
        period_days = {"1d": 1, "1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365}
        days = period_days.get(period, 30)

        candles = []
        sorted_dates = sorted(ts.keys(), reverse=True)[:days]
        for date_str in reversed(sorted_dates):
            entry = ts[date_str]
            candles.append({
                "timestamp": int(time.mktime(time.strptime(date_str, "%Y-%m-%d"))),
                "open": float(entry["1. open"]),
                "high": float(entry["2. high"]),
                "low": float(entry["3. low"]),
                "close": float(entry["4. close"]),
                "volume": int(entry["5. volume"]),
            })
        return {"symbol": ticker.upper(), "candles": candles}


def get_datasource_service(source: DataSource) -> BaseDataSource:
    name = source.name.lower()
    if "finnhub" in name:
        return FinnhubDataSource(source)
    elif "alpha" in name or "vantage" in name:
        return AlphaVantageDataSource(source)
    raise ValueError(f"Type de source inconnu : {source.name}")
