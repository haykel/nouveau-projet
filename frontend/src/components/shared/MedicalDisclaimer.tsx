"use client";

import { ShieldAlert } from "lucide-react";

export function MedicalDisclaimer({ className = "" }: { className?: string }) {
  return (
    <div
      className={`rounded-2xl border border-blue-100 bg-blue-50/60 px-6 py-4 text-sm text-blue-800 ${className}`}
    >
      <div className="flex items-start gap-3">
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-blue-500" />
        <p className="leading-relaxed">
          Ce service est un outil de <strong>pre-depistage</strong> et ne
          constitue en aucun cas un diagnostic medical. Seul un professionnel de
          sante qualifie peut realiser une evaluation clinique complete.
        </p>
      </div>
    </div>
  );
}
