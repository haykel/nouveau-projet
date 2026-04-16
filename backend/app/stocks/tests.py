import pandas as pd
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from app.stocks.services import FinnhubService, FinnhubServiceError, get_history_yfinance


@override_settings(FINNHUB_API_KEY="test-key")
@patch.object(FinnhubService, "_rate_limit")
class FinnhubServiceTest(SimpleTestCase):

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_success(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 150.0, "d": 2.5, "dp": 1.69,
            "h": 151.0, "l": 148.0, "o": 149.0, "pc": 147.5, "t": 1234567890,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        result = service.get_quote("AAPL")

        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["current_price"], 150.0)
        self.assertEqual(result["change"], 2.5)
        self.assertEqual(result["change_percent"], 1.69)
        mock_client.quote.assert_called_once_with("AAPL")

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_no_data(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {"c": 0, "d": 0, "dp": 0, "h": 0, "l": 0, "o": 0, "pc": 0}
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        with self.assertRaises(FinnhubServiceError) as ctx:
            service.get_quote("INVALID")
        self.assertIn("No data found", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_get_quote_api_error(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.side_effect = Exception("API timeout")
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        with self.assertRaises(FinnhubServiceError) as ctx:
            service.get_quote("AAPL")
        self.assertIn("Failed to fetch quote", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_search_symbol_success(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.symbol_lookup.return_value = {
            "count": 2,
            "result": [
                {"symbol": "AAPL", "description": "Apple Inc", "type": "Common Stock"},
                {"symbol": "AAPL.MX", "description": "Apple Inc", "type": "Common Stock"},
            ],
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.search_symbol("AAPL")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["symbol"], "AAPL")
        self.assertEqual(results[0]["description"], "Apple Inc")

    @patch("app.stocks.services.finnhub.Client")
    def test_search_symbol_empty(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.symbol_lookup.return_value = {"count": 0, "result": []}
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.search_symbol("XYZNONEXISTENT")
        self.assertEqual(results, [])

    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_success(self, mock_client_cls, mock_get, _mock_rl):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "Time Series (Daily)": {
                "2026-04-10": {"1. open": "100.0", "2. high": "102.0", "3. low": "99.0", "4. close": "101.0", "5. volume": "1000000"},
                "2026-04-11": {"1. open": "101.0", "2. high": "103.0", "3. low": "100.0", "4. close": "102.0", "5. volume": "1100000"},
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")

        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["candles"]), 2)
        self.assertEqual(result["candles"][0]["close"], 101.0)
        self.assertEqual(result["candles"][0]["volume"], 1000000)
        self.assertEqual(result["candles"][0]["time"], "2026-04-10")

    @patch("app.stocks.services.get_history_yfinance")
    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_alphavantage_quota_falls_back_to_yfinance(
        self, mock_client_cls, mock_get, mock_yf, _mock_rl
    ):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "Information": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day."
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        mock_yf.return_value = [
            {"time": "2026-04-10", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1000000},
        ]

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")

        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["candles"]), 1)
        self.assertEqual(result["candles"][0]["close"], 101.0)
        mock_yf.assert_called_once_with("AAPL", "1m")

    @patch("app.stocks.services.get_history_yfinance")
    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_alphavantage_note_falls_back_to_yfinance(
        self, mock_client_cls, mock_get, mock_yf, _mock_rl
    ):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "Note": "Thank you for using Alpha Vantage! Please limit to 5 API requests per minute."
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        mock_yf.return_value = [
            {"time": "2026-04-10", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1000000},
        ]

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")

        self.assertEqual(result["symbol"], "AAPL")
        mock_yf.assert_called_once_with("AAPL", "1m")

    @patch("app.stocks.services.get_history_yfinance")
    @patch("app.stocks.services.http_requests.get")
    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_no_data_falls_back_to_yfinance(
        self, mock_client_cls, mock_get, mock_yf, _mock_rl
    ):
        mock_client_cls.return_value = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"Meta Data": {}}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        mock_yf.return_value = [
            {"time": "2026-04-10", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1000000},
        ]

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            result = service.get_candles("AAPL", "1m")

        self.assertEqual(result["symbol"], "AAPL")
        mock_yf.assert_called_once_with("AAPL", "1m")

    @patch("app.stocks.services.finnhub.Client")
    def test_get_candles_invalid_period(self, mock_client_cls, _mock_rl):
        mock_client_cls.return_value = MagicMock()

        service = FinnhubService()
        with self.settings(ALPHA_VANTAGE_API_KEY="test-key"):
            with self.assertRaises(FinnhubServiceError) as ctx:
                service.get_candles("AAPL", "invalid")
        self.assertIn("Invalid period", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_get_market_indices(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 500.0, "d": 5.0, "dp": 1.0,
            "h": 505.0, "l": 495.0, "o": 498.0, "pc": 495.0, "t": 0,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.get_market_indices()

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "S&P 500")
        self.assertEqual(results[3]["name"], "CAC 40")

    @patch("app.stocks.services.finnhub.Client")
    def test_get_market_indices_partial_failure(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        call_count = 0

        def side_effect(ticker):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"c": 500.0, "d": 5.0, "dp": 1.0, "h": 505.0, "l": 495.0, "o": 498.0, "pc": 495.0, "t": 0}
            raise Exception("API error")

        mock_client.quote.side_effect = side_effect
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        results = service.get_market_indices()

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["current_price"], 500.0)
        self.assertIsNone(results[1]["current_price"])
        self.assertEqual(results[1]["error"], "Data unavailable")

    def test_missing_api_key_raises(self, _mock_rl):
        with self.settings(FINNHUB_API_KEY=""):
            with self.assertRaises(FinnhubServiceError) as ctx:
                FinnhubService()
            self.assertIn("not configured", str(ctx.exception))

    @patch("app.stocks.services.finnhub.Client")
    def test_ticker_uppercased(self, mock_client_cls, _mock_rl):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 150.0, "d": 2.5, "dp": 1.69,
            "h": 151.0, "l": 148.0, "o": 149.0, "pc": 147.5, "t": 0,
        }
        mock_client_cls.return_value = mock_client

        service = FinnhubService()
        result = service.get_quote("aapl")

        self.assertEqual(result["symbol"], "AAPL")
        mock_client.quote.assert_called_once_with("AAPL")


class YFinanceFallbackTest(SimpleTestCase):

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_success(self, mock_download):
        df = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [102.0, 103.0],
                "Low": [99.0, 100.0],
                "Close": [101.0, 102.0],
                "Volume": [1000000, 1100000],
            },
            index=pd.to_datetime(["2026-04-10", "2026-04-11"]),
        )
        mock_download.return_value = df

        result = get_history_yfinance("AAPL", "1m")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["time"], "2026-04-10")
        self.assertEqual(result[0]["close"], 101.0)
        self.assertEqual(result[1]["volume"], 1100000)
        mock_download.assert_called_once_with(
            "AAPL",
            period="1mo",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_empty(self, mock_download):
        mock_download.return_value = pd.DataFrame()

        result = get_history_yfinance("INVALID", "1m")
        self.assertEqual(result, [])

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_5y_period(self, mock_download):
        df = pd.DataFrame(
            {
                "Open": [50.0],
                "High": [55.0],
                "Low": [48.0],
                "Close": [52.0],
                "Volume": [5000000],
            },
            index=pd.to_datetime(["2021-04-01"]),
        )
        mock_download.return_value = df

        result = get_history_yfinance("AAPL", "5y")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["time"], "2021-04-01")
        mock_download.assert_called_once_with(
            "AAPL",
            period="5y",
            interval="1mo",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_api_error(self, mock_download):
        mock_download.side_effect = Exception("Network error")

        with self.assertRaises(FinnhubServiceError) as ctx:
            get_history_yfinance("AAPL", "1m")
        self.assertIn("Yahoo Finance failed", str(ctx.exception))

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_intraday_format(self, mock_download):
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [102.0],
                "Low": [99.0],
                "Close": [101.0],
                "Volume": [500000],
            },
            index=pd.to_datetime(["2026-04-10 09:30:00"]),
        )
        mock_download.return_value = df

        result = get_history_yfinance("AAPL", "1d")

        self.assertEqual(result[0]["time"], "2026-04-10 09:30:00")

    @patch("app.stocks.services.yf.download")
    def test_get_history_yfinance_1w_uses_60m_interval(self, mock_download):
        mock_download.return_value = pd.DataFrame()

        get_history_yfinance("AAPL", "1w")

        mock_download.assert_called_once_with(
            "AAPL",
            period="5d",
            interval="60m",
            auto_adjust=True,
            progress=False,
            threads=False,
        )
