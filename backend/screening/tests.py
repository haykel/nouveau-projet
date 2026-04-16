from django.test import TestCase, SimpleTestCase
from screening.services.safety_validation import SafetyValidationService
from screening.services.rule_engine import (
    RuleEngineService,
    HIGH_THRESHOLD,
    MEDIUM_THRESHOLD,
)


class SafetyValidationTest(SimpleTestCase):
    def setUp(self):
        self.service = SafetyValidationService()

    def test_blocks_diagnostic_language_fr(self):
        violations = self.service.validate_text("L'enfant a l'autisme")
        self.assertTrue(len(violations) > 0)

    def test_blocks_diagnostic_language_en(self):
        violations = self.service.validate_text("The child has autism")
        self.assertTrue(len(violations) > 0)

    def test_blocks_confirmation(self):
        violations = self.service.validate_text("Cela confirme l'autisme")
        self.assertTrue(len(violations) > 0)

    def test_allows_safe_language(self):
        safe_text = (
            "Ce depistage suggere un niveau de preoccupation modere. "
            "Une consultation est recommandee."
        )
        violations = self.service.validate_text(safe_text)
        self.assertEqual(len(violations), 0)

    def test_sanitize_adds_disclaimer(self):
        text = "Les reponses suggerent des preoccupations."
        result = self.service.sanitize_summary(text)
        self.assertIn("ne constitue pas un diagnostic", result)

    def test_sanitize_replaces_unsafe_text(self):
        text = "L'enfant a l'autisme et doit etre traite."
        result = self.service.sanitize_summary(text)
        self.assertNotIn("a l'autisme", result)
        self.assertIn("ne constitue pas un diagnostic", result)

    def test_validate_explanation_adds_disclaimer(self):
        explanation = {
            "summary": "Test summary",
            "details": "Test details",
        }
        result = self.service.validate_explanation(explanation)
        self.assertIn("disclaimer", result)

    def test_validate_explanation_blocks_unsafe_values(self):
        explanation = {
            "summary": "L'enfant a l'autisme",
            "details": "Safe details",
        }
        result = self.service.validate_explanation(explanation)
        self.assertNotIn("a l'autisme", result["summary"])


class RuleEngineThresholdsTest(SimpleTestCase):
    def test_thresholds_order(self):
        self.assertGreater(HIGH_THRESHOLD, MEDIUM_THRESHOLD)
        self.assertGreater(MEDIUM_THRESHOLD, 0)
        self.assertLess(HIGH_THRESHOLD, 1.0)
