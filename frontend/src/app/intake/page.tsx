"use client";

import { IntakeForm } from "@/components/intake/IntakeForm";
import { MedicalDisclaimer } from "@/components/shared/MedicalDisclaimer";

export default function IntakePage() {
  return (
    <div className="px-4 py-10">
      <div className="mx-auto mb-8 max-w-2xl text-center">
        <h1 className="mb-3 text-3xl font-bold tracking-tight text-gray-900">
          Informations de contact
        </h1>
        <p className="text-gray-500">
          Renseignez les informations necessaires pour personnaliser le
          questionnaire de depistage.
        </p>
      </div>
      <IntakeForm />
      <div className="mx-auto mt-10 max-w-2xl">
        <MedicalDisclaimer />
      </div>
    </div>
  );
}
