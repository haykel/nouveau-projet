"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Loader2,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Phone,
  MapPin,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionCard } from "@/components/shared/SectionCard";
import { MedicalDisclaimer } from "@/components/shared/MedicalDisclaimer";
import {
  DOMAIN_LABELS,
  RISK_LABELS,
  RISK_BG,
} from "@/lib/concerns";
import { api } from "@/lib/api";
import type { AnalysisResult } from "@/types";

const RISK_ICONS = {
  low: CheckCircle2,
  moderate: AlertCircle,
  high: AlertTriangle,
  very_high: XCircle,
};

export function ResultPage() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    api
      .getResults(sessionId)
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-sky-500" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="py-20 text-center text-red-500">
        {error || "Resultats non disponibles."}
      </div>
    );
  }

  const risk = RISK_LABELS[result.risk_level] || RISK_LABELS.low;
  const riskBg = RISK_BG[result.risk_level] || RISK_BG.low;
  const RiskIcon = RISK_ICONS[result.risk_level] || CheckCircle2;
  const explanation = result.explanation_json;

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 pb-16">
      <MedicalDisclaimer className="mb-2" />

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <SectionCard className={`border-2 ${riskBg}`}>
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white shadow-sm">
              <RiskIcon className={`h-6 w-6 ${risk.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">
                Niveau de preoccupation
              </p>
              <h2 className={`text-2xl font-bold ${risk.color}`}>
                {risk.label}
              </h2>
              <p className="mt-2 leading-relaxed text-gray-700">
                {explanation.summary}
              </p>
            </div>
          </div>
        </SectionCard>
      </motion.div>

      {/* Recommendation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <SectionCard>
          <h3 className="mb-3 text-lg font-semibold text-gray-900">
            Recommandation
          </h3>
          <p className="leading-relaxed text-gray-600">
            {explanation.nextSteps}
          </p>
        </SectionCard>
      </motion.div>

      {/* Domain scores */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <SectionCard>
          <h3 className="mb-5 text-lg font-semibold text-gray-900">
            Domaines evalues
          </h3>
          <div className="space-y-4">
            {Object.entries(result.domain_scores).map(([domain, scores]) => (
              <div key={domain}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-700">
                    {DOMAIN_LABELS[domain] || domain}
                  </span>
                  <span className="text-gray-400">
                    {scores.score} / {scores.max_score} ({scores.percentage}%)
                  </span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
                  <motion.div
                    className={`h-full rounded-full ${
                      scores.percentage >= 65
                        ? "bg-red-400"
                        : scores.percentage >= 40
                          ? "bg-amber-400"
                          : "bg-emerald-400"
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${scores.percentage}%` }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                  />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </motion.div>

      {/* AI Summary */}
      {result.ai_summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <SectionCard>
            <h3 className="mb-3 text-lg font-semibold text-gray-900">
              Resume detaille
            </h3>
            <p className="leading-relaxed text-gray-600">{result.ai_summary}</p>
          </SectionCard>
        </motion.div>
      )}

      {/* Red flags */}
      {result.red_flags.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <SectionCard className="border-orange-100 bg-orange-50/40">
            <h3 className="mb-3 text-lg font-semibold text-orange-800">
              Points d&apos;attention
            </h3>
            <ul className="space-y-2">
              {result.red_flags.map((flag) => (
                <li
                  key={flag}
                  className="flex items-center gap-2 text-sm text-orange-700"
                >
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  {flag.replace(/_/g, " ")}
                </li>
              ))}
            </ul>
          </SectionCard>
        </motion.div>
      )}

      {/* Providers */}
      {result.nearby_providers.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <SectionCard>
            <h3 className="mb-5 text-lg font-semibold text-gray-900">
              Professionnels a proximite
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              {result.nearby_providers.map((p) => (
                <div
                  key={p.id}
                  className="rounded-xl border border-gray-100 bg-gray-50/50 p-4 transition-shadow hover:shadow-sm"
                >
                  <h4 className="font-semibold text-gray-900">{p.name}</h4>
                  <p className="mt-0.5 text-sm font-medium text-sky-600">
                    {p.specialty}
                  </p>
                  <div className="mt-3 space-y-1.5 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-3.5 w-3.5" />
                      {p.address}, {p.city} &middot; {p.distance_km} km
                    </div>
                    {p.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="h-3.5 w-3.5" />
                        {p.phone}
                      </div>
                    )}
                  </div>
                  {p.phone && (
                    <a
                      href={`tel:${p.phone.replace(/\s/g, "")}`}
                      className="mt-3 flex w-full items-center justify-center rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
                    >
                      Appeler
                    </a>
                  )}
                </div>
              ))}
            </div>
          </SectionCard>
        </motion.div>
      )}

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="rounded-2xl bg-gray-50 p-6 text-center text-sm leading-relaxed text-gray-500"
      >
        {explanation.disclaimer}
      </motion.div>
    </div>
  );
}
