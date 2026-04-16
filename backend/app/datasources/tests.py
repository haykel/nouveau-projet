from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings

from app.datasources.models import DataSource
from app.datasources.router import DataSourceRouter, DataSourceError
from app.datasources.services import get_datasource_service, FinnhubDataSource, AlphaVantageDataSource


class DataSourceModelTest(TestCase):
    def test_api_key_encryption(self):
        ds = DataSource(name="Test")
        ds.api_key = "my-secret-key"
        self.assertNotEqual(ds._api_key, "my-secret-key")
        self.assertEqual(ds.api_key, "my-secret-key")

    def test_api_key_empty(self):
        ds = DataSource(name="Test")
        ds.api_key = ""
        self.assertEqual(ds.api_key, "")

    def test_quota_exceeded(self):
        ds = DataSource(name="Test", rate_limit_per_day=100, requests_today=100)
        self.assertTrue(ds.quota_exceeded)

    def test_quota_not_exceeded(self):
        ds = DataSource(name="Test", rate_limit_per_day=100, requests_today=50)
        self.assertFalse(ds.quota_exceeded)

    def test_str(self):
        ds = DataSource(name="Finnhub", priority=1, is_active=True, is_healthy=True)
        self.assertIn("Finnhub", str(ds))
        self.assertIn("active", str(ds))


class DataSourceRouterTest(TestCase):
    def setUp(self):
        self.finnhub = DataSource.objects.create(
            name="Finnhub",
            _api_key="dGVzdC1rZXk=",
            base_url="https://finnhub.io",
            is_active=True,
            priority=1,
            is_healthy=True,
            rate_limit_per_day=500,
        )
        self.alpha = DataSource.objects.create(
            name="AlphaVantage",
            _api_key="dGVzdC1rZXk=",
            base_url="https://www.alphavantage.co",
            is_active=True,
            priority=2,
            is_healthy=True,
            rate_limit_per_day=500,
        )
        self.router = DataSourceRouter()

    def test_get_active_source_returns_highest_priority(self):
        source = self.router.get_active_source()
        self.assertEqual(source.name, "Finnhub")

    def test_get_active_source_skips_unhealthy(self):
        self.finnhub.is_healthy = False
        self.finnhub.save()
        source = self.router.get_active_source()
        self.assertEqual(source.name, "AlphaVantage")

    def test_get_active_source_no_source_raises(self):
        DataSource.objects.all().update(is_active=False)
        with self.assertRaises(DataSourceError):
            self.router.get_active_source()

    def test_fallback_excludes_source(self):
        source = self.router.fallback(exclude_id=self.finnhub.id)
        self.assertEqual(source.name, "AlphaVantage")

    def test_fallback_no_source_raises(self):
        self.alpha.is_active = False
        self.alpha.save()
        with self.assertRaises(DataSourceError):
            self.router.fallback(exclude_id=self.finnhub.id)

    def test_record_request_increments(self):
        initial = self.finnhub.requests_today
        self.router.record_request(self.finnhub)
        self.finnhub.refresh_from_db()
        self.assertEqual(self.finnhub.requests_today, initial + 1)

    def test_is_quota_exceeded(self):
        self.finnhub.requests_today = 500
        self.finnhub.save()
        self.assertTrue(self.router.is_quota_exceeded(self.finnhub))

    def test_circuit_breaker_marks_unhealthy(self):
        for _ in range(3):
            self.router.record_error(self.finnhub)
        self.finnhub.refresh_from_db()
        self.assertFalse(self.finnhub.is_healthy)
        self.assertEqual(self.finnhub.consecutive_errors, 3)

    def test_circuit_breaker_resets_on_success(self):
        self.finnhub.consecutive_errors = 2
        self.finnhub.save()
        self.router.record_success(self.finnhub)
        self.finnhub.refresh_from_db()
        self.assertTrue(self.finnhub.is_healthy)
        self.assertEqual(self.finnhub.consecutive_errors, 0)

    def test_execute_with_fallback_success(self):
        result = self.router.execute_with_fallback(lambda src: f"ok-{src.name}")
        self.assertEqual(result, "ok-Finnhub")

    def test_execute_with_fallback_primary_fails(self):
        call_count = {"n": 0}

        def operation(src):
            call_count["n"] += 1
            if src.name == "Finnhub":
                raise Exception("Finnhub down")
            return f"ok-{src.name}"

        result = self.router.execute_with_fallback(operation)
        self.assertEqual(result, "ok-AlphaVantage")

    def test_execute_with_fallback_all_fail(self):
        def operation(src):
            raise Exception(f"{src.name} down")

        with self.assertRaises(DataSourceError):
            self.router.execute_with_fallback(operation)

    def test_execute_with_fallback_quota_exceeded_uses_fallback(self):
        self.finnhub.requests_today = 500
        self.finnhub.save()
        result = self.router.execute_with_fallback(lambda src: f"ok-{src.name}")
        self.assertEqual(result, "ok-AlphaVantage")


class DataSourceServicesTest(TestCase):
    def setUp(self):
        self.finnhub_src = DataSource.objects.create(
            name="Finnhub",
            _api_key="dGVzdC1rZXk=",
            base_url="https://finnhub.io",
            is_active=True,
            priority=1,
        )
        self.alpha_src = DataSource.objects.create(
            name="AlphaVantage",
            _api_key="dGVzdC1rZXk=",
            base_url="https://www.alphavantage.co",
            is_active=True,
            priority=2,
        )

    def test_get_datasource_service_finnhub(self):
        svc = get_datasource_service(self.finnhub_src)
        self.assertIsInstance(svc, FinnhubDataSource)

    def test_get_datasource_service_alpha(self):
        svc = get_datasource_service(self.alpha_src)
        self.assertIsInstance(svc, AlphaVantageDataSource)

    def test_get_datasource_service_unknown(self):
        unknown = DataSource.objects.create(name="Unknown", priority=3)
        with self.assertRaises(ValueError):
            get_datasource_service(unknown)

    @patch("app.datasources.services.finnhub.Client")
    def test_finnhub_get_quote(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.quote.return_value = {
            "c": 150.0, "d": 2.5, "dp": 1.69,
            "h": 151.0, "l": 148.0, "o": 149.0, "pc": 147.5, "t": 12345,
        }
        mock_client_cls.return_value = mock_client

        svc = FinnhubDataSource(self.finnhub_src)
        result = svc.get_quote("AAPL")
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["current_price"], 150.0)

    @patch("app.datasources.services.http_requests.get")
    def test_alpha_get_quote(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "Global Quote": {
                "01. symbol": "AAPL",
                "02. open": "149.0",
                "03. high": "151.0",
                "04. low": "148.0",
                "05. price": "150.0",
                "08. previous close": "147.5",
                "09. change": "2.5",
                "10. change percent": "1.69%",
            }
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        svc = AlphaVantageDataSource(self.alpha_src)
        result = svc.get_quote("AAPL")
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["current_price"], 150.0)
        self.assertEqual(result["change_percent"], 1.69)
