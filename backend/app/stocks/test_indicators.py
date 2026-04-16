from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings

from app.stocks.indicators import TechnicalIndicators


class MATest(SimpleTestCase):
    def test_ma_basic(self):
        prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = TechnicalIndicators.calculate_ma(prices, 3)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertAlmostEqual(result[2], 2.0)
        self.assertAlmostEqual(result[9], 9.0)

    def test_ma_period_exceeds_length(self):
        result = TechnicalIndicators.calculate_ma([1, 2], 5)
        self.assertEqual(result, [None, None])

    def test_ema_basic(self):
        prices = [22, 22.27, 22.19, 22.08, 22.17, 22.18, 22.13, 22.23, 22.43, 22.24]
        result = TechnicalIndicators.calculate_ema(prices, 5)
        self.assertIsNone(result[0])
        self.assertIsNotNone(result[4])
        self.assertEqual(len(result), len(prices))


class RSITest(SimpleTestCase):
    def test_rsi_length(self):
        prices = list(range(1, 31))
        result = TechnicalIndicators.calculate_rsi(prices, 14)
        self.assertEqual(len(result), len(prices))

    def test_rsi_first_values_none(self):
        prices = list(range(1, 31))
        result = TechnicalIndicators.calculate_rsi(prices, 14)
        for i in range(14):
            self.assertIsNone(result[i])
        self.assertIsNotNone(result[14])

    def test_rsi_constant_rise(self):
        prices = list(range(1, 31))
        result = TechnicalIndicators.calculate_rsi(prices, 14)
        rsi = result[-1]
        self.assertAlmostEqual(rsi, 100.0)

    def test_rsi_too_few_prices(self):
        result = TechnicalIndicators.calculate_rsi([50, 51, 52], 14)
        self.assertTrue(all(v is None for v in result))

    def test_rsi_range(self):
        prices = [100 + (i % 7) * (-1) ** i for i in range(50)]
        result = TechnicalIndicators.calculate_rsi(prices, 14)
        for v in result:
            if v is not None:
                self.assertGreaterEqual(v, 0)
                self.assertLessEqual(v, 100)


class MACDTest(SimpleTestCase):
    def test_macd_structure(self):
        prices = [100 + i * 0.5 for i in range(50)]
        result = TechnicalIndicators.calculate_macd(prices)
        self.assertIn("macd", result)
        self.assertIn("signal", result)
        self.assertIn("histogram", result)
        self.assertEqual(len(result["macd"]), len(prices))

    def test_macd_early_values_none(self):
        prices = [100 + i * 0.5 for i in range(50)]
        result = TechnicalIndicators.calculate_macd(prices)
        self.assertIsNone(result["macd"][0])


class BollingerTest(SimpleTestCase):
    def test_bollinger_structure(self):
        prices = [100 + i * 0.5 for i in range(30)]
        result = TechnicalIndicators.calculate_bollinger_bands(prices, 20)
        self.assertIn("upper", result)
        self.assertIn("middle", result)
        self.assertIn("lower", result)

    def test_bollinger_bands_ordering(self):
        prices = [100 + i * 0.5 for i in range(30)]
        result = TechnicalIndicators.calculate_bollinger_bands(prices, 20)
        for u, m, lo in zip(result["upper"], result["middle"], result["lower"]):
            if u is not None:
                self.assertGreaterEqual(u, m)
                self.assertGreaterEqual(m, lo)

    def test_bollinger_early_none(self):
        prices = [100 + i * 0.5 for i in range(30)]
        result = TechnicalIndicators.calculate_bollinger_bands(prices, 20)
        for i in range(19):
            self.assertIsNone(result["upper"][i])
        self.assertIsNotNone(result["upper"][19])


class VolumeProfileTest(SimpleTestCase):
    def test_volume_profile_bins(self):
        prices = [100, 101, 102, 103, 104, 105]
        volumes = [1000, 2000, 3000, 4000, 5000, 6000]
        result = TechnicalIndicators.calculate_volume_profile(prices, volumes, bins=5)
        self.assertEqual(len(result), 5)
        self.assertIn("price", result[0])
        self.assertIn("volume", result[0])

    def test_volume_profile_empty(self):
        result = TechnicalIndicators.calculate_volume_profile([], [])
        self.assertEqual(result, [])


class ScoreTest(SimpleTestCase):
    def test_score_insufficient_data(self):
        result = TechnicalIndicators.calculate_score([100, 101], [1000, 1100])
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["signal"], "NEUTRE")

    def test_score_structure(self):
        prices = [100 + i * 0.5 for i in range(60)]
        volumes = [1000000 + i * 10000 for i in range(60)]
        result = TechnicalIndicators.calculate_score(prices, volumes)
        self.assertIn("score", result)
        self.assertIn("signal", result)
        self.assertIn("explanation", result)
        self.assertIn("details", result)
        self.assertIn(result["signal"], ["ACHAT", "NEUTRE", "VENTE"])
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_score_uptrend_bullish(self):
        prices = [50 + i * 1.5 for i in range(60)]
        volumes = [1000000 + i * 50000 for i in range(60)]
        result = TechnicalIndicators.calculate_score(prices, volumes)
        self.assertGreaterEqual(result["score"], 40)

    def test_score_downtrend_bearish(self):
        prices = [200 - i * 1.5 for i in range(60)]
        volumes = [1000000 - i * 10000 for i in range(60)]
        result = TechnicalIndicators.calculate_score(prices, volumes)
        self.assertLessEqual(result["score"], 60)
