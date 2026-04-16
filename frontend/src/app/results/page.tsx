"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { ResultPage } from "@/components/results/ResultPage";

export default function ResultsPage() {
  return (
    <div className="py-10">
      <div className="mx-auto mb-8 max-w-3xl px-4 text-center">
        <h1 className="mb-3 text-3xl font-bold tracking-tight text-gray-900">
          Resultats du pre-depistage
        </h1>
        <p className="text-gray-500">
          Voici une synthese basee sur vos reponses au questionnaire.
        </p>
      </div>
      <Suspense
        fallback={
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-sky-500" />
          </div>
        }
      >
        <ResultPage />
      </Suspense>
    </div>
  );
}
