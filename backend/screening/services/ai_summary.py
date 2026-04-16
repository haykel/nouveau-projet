import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a medical pre-screening assistant for Autism Spectrum Disorder (ASD) in children.
You help generate parent-friendly summaries based on structured screening results.

STRICT RULES:
- You must NEVER diagnose ASD or any condition.
- You must NEVER state that a child "has" or "does not have" autism.
- You must NEVER express medical certainty.
- You must NEVER override clinical red flags or scoring thresholds.
- You must ALWAYS recommend professional consultation when risk is moderate or above.
- You must ALWAYS include a disclaimer that this is not a diagnosis.

Your role is to:
1. Summarize findings in clear, empathetic language for parents.
2. Explain which developmental areas show concerns.
3. Provide actionable next steps.
4. Generate a structured narrative for clinician handoff.

Respond in French. Be empathetic, clear, and medically responsible.
"""


class AISummaryService:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY

    def generate_summary(self, child_age_months, concerns, domain_scores,
                         red_flags, recommendation_level):
        if not self.api_key:
            return self._fallback_summary(
                domain_scores, red_flags, recommendation_level
            )

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            user_prompt = self._build_prompt(
                child_age_months, concerns, domain_scores,
                red_flags, recommendation_level
            )

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text

        except Exception as e:
            logger.error("AI summary generation failed: %s", e)
            return self._fallback_summary(
                domain_scores, red_flags, recommendation_level
            )

    def _build_prompt(self, child_age_months, concerns, domain_scores,
                      red_flags, recommendation_level):
        lines = [
            f"Age de l'enfant : {child_age_months} mois",
            f"Preoccupations principales : {', '.join(concerns) if concerns else 'Aucune specifiee'}",
            "",
            "Scores par domaine :",
        ]
        for domain, scores in domain_scores.items():
            lines.append(
                f"  - {domain}: {scores['score']}/{scores['max_score']} "
                f"({scores['percentage']}%)"
            )

        lines.append("")
        if red_flags:
            lines.append(f"Signaux d'alerte detectes : {', '.join(red_flags)}")
        else:
            lines.append("Aucun signal d'alerte critique detecte.")

        lines.append(f"Niveau de recommandation : {recommendation_level}")
        lines.append("")
        lines.append(
            "Genere un resume structure avec : "
            "1) Resume pour les parents, "
            "2) Details des preoccupations, "
            "3) Prochaines etapes recommandees, "
            "4) Avertissement medical."
        )
        return "\n".join(lines)

    def _fallback_summary(self, domain_scores, red_flags, recommendation_level):
        parts = []

        concern_domains = [
            d for d, s in domain_scores.items() if s.get("percentage", 0) >= 40
        ]

        if concern_domains:
            parts.append(
                "Les reponses indiquent des preoccupations dans les domaines suivants : "
                f"{', '.join(concern_domains)}."
            )
        else:
            parts.append(
                "Les reponses ne suggerent pas de preoccupations significatives "
                "dans les domaines evalues."
            )

        if red_flags:
            parts.append(
                f"Signaux d'alerte detectes : {', '.join(red_flags)}. "
                "Ces elements justifient une evaluation approfondie."
            )

        recommendations = {
            "monitor": "Un suivi regulier du developpement est recommande.",
            "pediatric_consultation": (
                "Une consultation pediatrique est recommandee pour "
                "evaluer le developpement de l'enfant."
            ),
            "specialist_consultation": (
                "Une consultation specialisee (neuropediatre, pedopsychiatre) "
                "est recommandee."
            ),
            "urgent_referral": (
                "Une orientation urgente vers un specialiste du developpement "
                "est fortement recommandee."
            ),
        }
        parts.append(
            recommendations.get(recommendation_level, recommendations["monitor"])
        )

        parts.append(
            "Ce resultat ne constitue pas un diagnostic. "
            "Seul un professionnel de sante qualifie peut realiser "
            "une evaluation clinique complete."
        )

        return " ".join(parts)
