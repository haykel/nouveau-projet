"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence } from "framer-motion";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProgressBar } from "@/components/shared/ProgressBar";
import { QuestionCard } from "./QuestionCard";
import { api } from "@/lib/api";
import type { Question, AnswerPayload } from "@/types";

export function QuestionnaireFlow() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Map<number, AnswerPayload>>(new Map());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    api
      .getQuestions(sessionId)
      .then((data) => {
        const seen = new Set<number>();
        const unique: Question[] = [];
        for (const block of data.blocks) {
          for (const q of block.questions) {
            if (!seen.has(q.id)) {
              seen.add(q.id);
              unique.push(q);
            }
          }
        }
        setQuestions(unique);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  const handleSelect = useCallback(
    (optionId: number, value: string) => {
      const q = questions[currentIdx];
      const updated = new Map(answers);
      updated.set(q.id, {
        question_id: q.id,
        selected_option_id: optionId,
        raw_value: value,
      });
      setAnswers(updated);

      // Auto-advance after a brief delay
      setTimeout(() => {
        if (currentIdx < questions.length - 1) {
          setCurrentIdx((i) => i + 1);
        }
      }, 350);
    },
    [answers, currentIdx, questions]
  );

  const handleSubmit = async () => {
    if (!sessionId) return;
    setSubmitting(true);
    setError("");
    try {
      await api.submitAnswers(sessionId, Array.from(answers.values()));
      await api.analyze(sessionId);
      router.push(`/results?session=${sessionId}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur lors de l'analyse");
      setSubmitting(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="py-20 text-center text-gray-500">
        Session invalide.{" "}
        <button
          onClick={() => router.push("/intake")}
          className="text-sky-600 underline"
        >
          Recommencer
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-sky-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center text-red-500">
        {error}
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-20 text-center">
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-8">
          <h3 className="mb-2 text-lg font-semibold text-amber-800">
            Aucune question disponible
          </h3>
          <p className="mb-4 text-sm text-amber-700">
            Aucun questionnaire n&apos;est disponible pour la tranche d&apos;age indiquee.
            Ce service couvre les enfants de 9 mois a 12 ans.
          </p>
          <button
            onClick={() => router.push("/intake")}
            className="rounded-xl bg-amber-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-amber-700"
          >
            Modifier les informations
          </button>
        </div>
      </div>
    );
  }

  const current = questions[currentIdx];
  const isLast = currentIdx === questions.length - 1;
  const allAnswered = answers.size === questions.length;

  return (
    <div className="mx-auto max-w-2xl px-4">
      <ProgressBar current={currentIdx + 1} total={questions.length} />

      <div className="mt-10">
        <AnimatePresence mode="wait">
          {current && (
            <QuestionCard
              key={current.id}
              question={current}
              selectedOptionId={answers.get(current.id)?.selected_option_id ?? null}
              onSelect={handleSelect}
            />
          )}
        </AnimatePresence>
      </div>

      <div className="mt-10 flex items-center justify-between">
        <Button
          type="button"
          variant="ghost"
          onClick={() => setCurrentIdx((i) => Math.max(i - 1, 0))}
          disabled={currentIdx === 0}
          className="rounded-xl"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Precedent
        </Button>

        {isLast && allAnswered && (
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 px-6"
          >
            {submitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyse en cours...
              </>
            ) : (
              "Voir les resultats"
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
