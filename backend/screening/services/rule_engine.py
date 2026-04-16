from screening.models import Answer, Question


RED_FLAG_CODES = {
    "language_regression": "Regression langagiere",
    "social_regression": "Regression sociale",
    "no_response_to_name": "Absence de reponse au prenom",
    "no_pointing": "Absence de pointage",
    "no_joint_attention": "Absence d'attention conjointe",
    "no_single_words_at_24_months": "Pas de mots isoles a 24 mois",
    "no_phrases_at_36_months": "Pas de phrases a 36 mois",
    "loss_of_skills": "Perte de competences acquises",
}

URGENT_FLAGS = {"language_regression", "social_regression", "loss_of_skills"}

HIGH_THRESHOLD = 0.65
MEDIUM_THRESHOLD = 0.40


class RuleEngineService:
    def __init__(self, session):
        self.session = session
        self.answers = list(
            Answer.objects.filter(session=session)
            .select_related("question", "selected_option")
        )

    def compute(self):
        domain_scores = self._compute_domain_scores()
        red_flags = self._detect_red_flags()
        global_score = self._compute_global_score(domain_scores)
        max_possible = self._compute_max_possible()
        score_ratio = global_score / max_possible if max_possible > 0 else 0
        recommendation = self._determine_recommendation(red_flags, score_ratio)
        risk_level = self._determine_risk_level(red_flags, score_ratio)

        return {
            "global_score": round(global_score, 2),
            "domain_scores": domain_scores,
            "red_flags": red_flags,
            "recommendation_level": recommendation,
            "risk_level": risk_level,
        }

    def _compute_domain_scores(self):
        domains = {}
        for answer in self.answers:
            domain = answer.question.domain
            if domain not in domains:
                domains[domain] = {"score": 0, "max_score": 0, "count": 0}
            weight = answer.question.score_weight
            domains[domain]["score"] += answer.computed_score * weight
            max_option_score = (
                answer.question.options.order_by("-score").values_list("score", flat=True).first() or 0
            )
            domains[domain]["max_score"] += max_option_score * weight
            domains[domain]["count"] += 1

        result = {}
        for domain, data in domains.items():
            max_s = data["max_score"]
            result[domain] = {
                "score": round(data["score"], 2),
                "max_score": round(max_s, 2),
                "percentage": round(data["score"] / max_s * 100, 1) if max_s > 0 else 0,
            }
        return result

    def _detect_red_flags(self):
        flags = []
        for answer in self.answers:
            if answer.selected_option and answer.selected_option.is_red_flag:
                flag_code = answer.question.trigger_flag
                if flag_code and flag_code not in flags:
                    flags.append(flag_code)
        return flags

    def _compute_global_score(self, domain_scores):
        return sum(d["score"] for d in domain_scores.values())

    def _compute_max_possible(self):
        total = 0
        for answer in self.answers:
            max_score = (
                answer.question.options.order_by("-score").values_list("score", flat=True).first() or 0
            )
            total += max_score * answer.question.score_weight
        return total

    def _determine_recommendation(self, red_flags, score_ratio):
        if any(f in URGENT_FLAGS for f in red_flags):
            return "urgent_referral"
        if score_ratio >= HIGH_THRESHOLD:
            return "specialist_consultation"
        if score_ratio >= MEDIUM_THRESHOLD:
            return "pediatric_consultation"
        return "monitor"

    def _determine_risk_level(self, red_flags, score_ratio):
        if any(f in URGENT_FLAGS for f in red_flags):
            return "very_high"
        if score_ratio >= HIGH_THRESHOLD:
            return "high"
        if score_ratio >= MEDIUM_THRESHOLD:
            return "moderate"
        return "low"
