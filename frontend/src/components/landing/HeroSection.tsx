"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Shield, Clock, FileCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-4 pb-20 pt-16 md:pt-24">
      {/* Background gradient */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-40 left-1/2 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-gradient-to-br from-sky-100/60 via-teal-50/40 to-transparent blur-3xl" />
      </div>

      <div className="mx-auto max-w-3xl text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="mb-6 inline-block rounded-full border border-sky-200 bg-sky-50 px-4 py-1.5 text-sm font-medium text-sky-700">
            Pre-depistage en ligne
          </span>
        </motion.div>

        <motion.h1
          className="mb-6 text-4xl font-bold tracking-tight text-gray-900 md:text-5xl lg:text-6xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Evaluez le developpement{" "}
          <span className="bg-gradient-to-r from-sky-500 to-teal-500 bg-clip-text text-transparent">
            de votre enfant
          </span>
        </motion.h1>

        <motion.p
          className="mx-auto mb-10 max-w-xl text-lg leading-relaxed text-gray-500"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Un questionnaire de pre-depistage simple et confidentiel pour identifier
          d&apos;eventuelles preoccupations liees au developpement de votre enfant
          et vous orienter vers les bons professionnels.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Link href="/intake">
            <Button
              size="lg"
              className="h-14 rounded-2xl bg-gradient-to-r from-sky-500 to-teal-500 px-8 text-base font-semibold shadow-lg shadow-sky-200/50 transition-all hover:shadow-xl hover:shadow-sky-200/60"
            >
              Commencer le depistage
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </motion.div>
      </div>

      {/* Steps */}
      <motion.div
        className="mx-auto mt-20 grid max-w-4xl gap-6 md:grid-cols-3"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        {[
          {
            icon: FileCheck,
            title: "1. Remplissez le formulaire",
            desc: "Quelques informations sur votre enfant et vos preoccupations.",
          },
          {
            icon: Clock,
            title: "2. Repondez aux questions",
            desc: "Un questionnaire adapte a l'age, en 10 a 15 minutes.",
          },
          {
            icon: Shield,
            title: "3. Recevez une orientation",
            desc: "Un rapport structure avec des recommandations claires.",
          },
        ].map((step) => (
          <div
            key={step.title}
            className="group rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-500 transition-colors group-hover:bg-sky-100">
              <step.icon className="h-6 w-6" />
            </div>
            <h3 className="mb-2 font-semibold text-gray-900">{step.title}</h3>
            <p className="text-sm leading-relaxed text-gray-500">{step.desc}</p>
          </div>
        ))}
      </motion.div>
    </section>
  );
}
