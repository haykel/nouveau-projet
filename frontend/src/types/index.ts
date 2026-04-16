export interface ScreeningSession {
  id: string;
  parent_name: string;
  child_first_name: string;
  child_age_months: number;
  child_sex: "M" | "F";
  respondent_role: string;
  main_concerns: string[];
  address: string;
  postal_code: string;
  city: string;
  lat: number | null;
  lng: number | null;
  created_at: string;
}

export interface SessionCreatePayload {
  parent_name: string;
  child_first_name: string;
  child_age_months: number;
  child_sex: "M" | "F";
  respondent_role: string;
  main_concerns: string[];
  address?: string;
  postal_code?: string;
  city?: string;
  lat?: number;
  lng?: number;
}

export interface QuestionOption {
  id: number;
  label: string;
  value: string;
  score: number;
  is_red_flag: boolean;
  order_index: number;
}

export interface Question {
  id: number;
  code: string;
  name: string;
  text: string;
  description: string;
  question_type: string;
  domain: string;
  score_weight: number;
  age_min_months: number;
  age_max_months: number;
  trigger_flag: string;
  options: QuestionOption[];
}

export interface QuestionBlock {
  id: number;
  code: string;
  name: string;
  is_core: boolean;
  questions: Question[];
}

export interface AnswerPayload {
  question_id: number;
  selected_option_id: number;
  raw_value: string;
}

export interface DomainScore {
  score: number;
  max_score: number;
  percentage: number;
}

export interface ExplanationJson {
  summary: string;
  details: string;
  nextSteps: string;
  disclaimer: string;
}

export interface Provider {
  id: number;
  name: string;
  specialty: string;
  address: string;
  city: string;
  postal_code: string;
  phone: string;
  distance_km: number;
}

export interface AnalysisResult {
  id: string;
  session_id: string;
  global_score: number;
  risk_level: "low" | "moderate" | "high" | "very_high";
  recommendation_level: string;
  red_flags: string[];
  domain_scores: Record<string, DomainScore>;
  ai_summary: string;
  ai_confidence_notes: string[];
  explanation_json: ExplanationJson;
  created_at: string;
  nearby_providers: Provider[];
}
