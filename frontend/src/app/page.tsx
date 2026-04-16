"use client";

import { HeroSection } from "@/components/landing/HeroSection";
import { TrustSection } from "@/components/landing/TrustSection";
import { MedicalDisclaimer } from "@/components/shared/MedicalDisclaimer";

export default function Home() {
  return (
    <>
      <HeroSection />
      <TrustSection />
      <div className="mx-auto max-w-3xl px-4 pb-16">
        <MedicalDisclaimer />
      </div>
    </>
  );
}
