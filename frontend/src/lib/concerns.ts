export const CONCERN_OPTIONS = [
  { value: "language_delay", label: "Retard de langage" },
  { value: "no_eye_contact", label: "Pas de contact visuel" },
  { value: "no_response_to_name", label: "Ne repond pas au prenom" },
  { value: "repetitive_behavior", label: "Comportements repetitifs" },
  { value: "social_difficulty", label: "Difficultes sociales" },
  { value: "sensory_sensitivity", label: "Sensibilite sensorielle" },
  { value: "regression", label: "Perte de competences acquises" },
  { value: "other", label: "Autre" },
] as const;

export const DOMAIN_LABELS: Record<string, string> = {
  communication: "Communication",
  social_interaction: "Interaction sociale",
  behavior: "Comportements",
  sensory: "Sensoriel",
  motor: "Motricite",
  autonomy: "Autonomie",
};

export const RISK_LABELS: Record<string, { label: string; color: string }> = {
  low: { label: "Faible", color: "text-emerald-600" },
  moderate: { label: "Modere", color: "text-amber-600" },
  high: { label: "Eleve", color: "text-orange-600" },
  very_high: { label: "Tres eleve", color: "text-red-600" },
};

export const RISK_BG: Record<string, string> = {
  low: "bg-emerald-50 border-emerald-200",
  moderate: "bg-amber-50 border-amber-200",
  high: "bg-orange-50 border-orange-200",
  very_high: "bg-red-50 border-red-200",
};
