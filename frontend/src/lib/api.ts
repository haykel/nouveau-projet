import type {
  ScreeningSession,
  SessionCreatePayload,
  QuestionBlock,
  AnswerPayload,
  AnalysisResult,
  Provider,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  createSession(data: SessionCreatePayload) {
    return request<ScreeningSession>("/api/sessions/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getQuestions(sessionId: string) {
    return request<{ blocks: QuestionBlock[] }>(
      `/api/sessions/${sessionId}/questions/`
    );
  },

  submitAnswers(sessionId: string, answers: AnswerPayload[]) {
    return request<{ submitted: number; answer_ids: string[] }>(
      `/api/sessions/${sessionId}/answers/`,
      { method: "POST", body: JSON.stringify({ answers }) }
    );
  },

  analyze(sessionId: string) {
    return request<AnalysisResult>(
      `/api/sessions/${sessionId}/analyze/`,
      { method: "POST" }
    );
  },

  getResults(sessionId: string) {
    return request<AnalysisResult>(
      `/api/sessions/${sessionId}/results/`
    );
  },

  getNearbyProviders(lat: number, lng: number, radius?: number) {
    const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
    if (radius) params.set("radius", String(radius));
    return request<Provider[]>(`/api/providers/nearby/?${params}`);
  },
};
