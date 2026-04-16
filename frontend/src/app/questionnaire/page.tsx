"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { QuestionnaireFlow } from "@/components/questionnaire/QuestionnaireFlow";

export default function QuestionnairePage() {
  return (
    <div className="py-10">
      <Suspense
        fallback={
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-sky-500" />
          </div>
        }
      >
        <QuestionnaireFlow />
      </Suspense>
    </div>
  );
}
