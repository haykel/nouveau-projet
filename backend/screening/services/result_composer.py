from screening.models import AnalysisResult
from .rule_engine import RuleEngineService, RED_FLAG_CODES
from .ai_summary import AISummaryService
from .safety_validation import SafetyValidationService
from .provider_matcher import ProviderMatcherService


class ResultComposerService:
    def __init__(self, session):
        self.session = session

    def analyze(self):
        # Layer 1: Rule-based clinical engine
        engine = RuleEngineService(self.session)
        engine_result = engine.compute()

        # Layer 2: AI interpretation
        ai_service = AISummaryService()
        raw_summary = ai_service.generate_summary(
            child_age_months=self.session.child_age_months,
            concerns=self.session.main_concerns,
            domain_scores=engine_result["domain_scores"],
            red_flags=engine_result["red_flags"],
            recommendation_level=engine_result["recommendation_level"],
        )

        # Layer 3: Safety validation
        safety = SafetyValidationService()
        safe_summary = safety.sanitize_summary(raw_summary)

        explanation = self._build_explanation(engine_result)
        safe_explanation = safety.validate_explanation(explanation)

        # Persist result
        result, _ = AnalysisResult.objects.update_or_create(
            session=self.session,
            defaults={
                "global_score": engine_result["global_score"],
                "risk_level": engine_result["risk_level"],
                "recommendation_level": engine_result["recommendation_level"],
                "red_flags": engine_result["red_flags"],
                "domain_scores": engine_result["domain_scores"],
                "ai_summary": safe_summary,
                "explanation_json": safe_explanation,
            },
        )

        # Provider matching
        providers = []
        if engine_result["recommendation_level"] != "monitor":
            matcher = ProviderMatcherService()
            providers = matcher.find_nearby(
                self.session.lat, self.session.lng
            )

        return result, providers

    def _build_explanation(self, engine_result):
        risk = engine_result["risk_level"]
        recommendation = engine_result["recommendation_level"]
        red_flags = engine_result["red_flags"]

        summaries = {
            "low": "Ce depistage ne suggere pas de preoccupation significative.",
            "moderate": "Ce depistage suggere un niveau de preoccupation modere.",
            "high": "Ce depistage suggere un niveau de preoccupation eleve.",
            "very_high": "Ce depistage suggere un niveau de preoccupation tres eleve.",
        }

        next_steps = {
            "monitor": (
                "Continuez a observer le developpement de votre enfant. "
                "N'hesitez pas a consulter si de nouvelles preoccupations apparaissent."
            ),
            "pediatric_consultation": (
                "Nous recommandons de consulter votre pediatre pour discuter "
                "de ces observations et evaluer le developpement de votre enfant."
            ),
            "specialist_consultation": (
                "Nous recommandons de consulter un specialiste du developpement "
                "de l'enfant (neuropediatre, pedopsychiatre) dans les prochaines semaines."
            ),
            "urgent_referral": (
                "Nous recommandons de prendre rendez-vous rapidement avec un specialiste "
                "du developpement de l'enfant pour une evaluation approfondie."
            ),
        }

        details_parts = []
        concern_domains = [
            d for d, s in engine_result["domain_scores"].items()
            if s.get("percentage", 0) >= 40
        ]
        if concern_domains:
            details_parts.append(
                "Des indicateurs dans les domaines suivants suggerent "
                f"qu'une evaluation serait benefique : {', '.join(concern_domains)}."
            )
        if red_flags:
            readable = [RED_FLAG_CODES.get(f, f) for f in red_flags]
            details_parts.append(
                f"Signaux d'alerte releves : {', '.join(readable)}."
            )

        return {
            "summary": summaries.get(risk, summaries["low"]),
            "details": " ".join(details_parts) if details_parts else (
                "Aucune preoccupation majeure n'a ete identifiee."
            ),
            "nextSteps": next_steps.get(recommendation, next_steps["monitor"]),
            "disclaimer": (
                "Ce resultat ne constitue pas un diagnostic. "
                "Seul un professionnel de sante qualifie peut realiser "
                "une evaluation clinique complete."
            ),
        }
