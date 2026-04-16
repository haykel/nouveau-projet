import re

FORBIDDEN_PATTERNS = [
    r"\b(a|has|have|got)\s+(l['\u2019])?autisme\b",
    r"\bl['\u2019]enfant\s+(est|a)\s+autiste\b",
    r"\bconfirme\s+(l['\u2019])?autisme\b",
    r"\bdiagnostic\s+(d['\u2019])?autisme\b",
    r"\bn['\u2019]a\s+pas\s+(l['\u2019])?autisme\b",
    r"\bhas\s+autism\b",
    r"\bdoes\s+not\s+have\s+autism\b",
    r"\bconfirms?\s+autism\b",
    r"\bdiagnosed?\s+with\s+autism\b",
    r"\bis\s+autistic\b",
    r"\bis\s+not\s+autistic\b",
    r"\bcertitude\s+medicale\b",
    r"\bcertitude\s+diagnostique\b",
    r"\bsans\s+aucun\s+doute\b",
    r"\bcertainement\s+autiste\b",
    r"\btype\s+d['\u2019]autisme\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]

MANDATORY_DISCLAIMER = (
    "Ce resultat ne constitue pas un diagnostic. "
    "Seul un professionnel de sante qualifie peut realiser "
    "une evaluation clinique complete."
)


class SafetyValidationService:
    def validate_text(self, text):
        violations = []
        for pattern in COMPILED_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                violations.append({
                    "pattern": pattern.pattern,
                    "matches": matches,
                })
        return violations

    def sanitize_summary(self, text):
        violations = self.validate_text(text)
        if violations:
            return self._generate_safe_replacement(text)
        if MANDATORY_DISCLAIMER not in text:
            text = text.rstrip() + "\n\n" + MANDATORY_DISCLAIMER
        return text

    def validate_explanation(self, explanation_dict):
        safe = {}
        for key, value in explanation_dict.items():
            if isinstance(value, str):
                violations = self.validate_text(value)
                if violations:
                    safe[key] = self._safe_fallback_for_key(key)
                else:
                    safe[key] = value
            else:
                safe[key] = value

        if "disclaimer" not in safe or not safe["disclaimer"]:
            safe["disclaimer"] = MANDATORY_DISCLAIMER
        return safe

    def _generate_safe_replacement(self, original_text):
        return (
            "Les reponses au questionnaire de depistage suggerent "
            "des preoccupations dans certains domaines du developpement. "
            "Une evaluation professionnelle est recommandee pour approfondir "
            "ces observations. " + MANDATORY_DISCLAIMER
        )

    def _safe_fallback_for_key(self, key):
        fallbacks = {
            "summary": (
                "Ce depistage suggere des preoccupations dans certains "
                "domaines du developpement."
            ),
            "details": (
                "Certains indicateurs justifient une evaluation "
                "professionnelle approfondie."
            ),
            "nextSteps": (
                "Nous recommandons de consulter un professionnel de sante "
                "specialise dans le developpement de l'enfant."
            ),
            "disclaimer": MANDATORY_DISCLAIMER,
        }
        return fallbacks.get(key, fallbacks["summary"])
