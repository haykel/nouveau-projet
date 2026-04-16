from django.test import SimpleTestCase, RequestFactory
from app.views import health


class HealthTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_health_returns_ok(self):
        request = self.factory.get("/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})
