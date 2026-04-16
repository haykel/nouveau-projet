"use client";

import { motion } from "framer-motion";
import { Lock, Brain, Stethoscope, ShieldCheck } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Base scientifique",
    desc: "Questionnaire inspire des outils valides de depistage (M-CHAT-R, ASQ).",
  },
  {
    icon: ShieldCheck,
    title: "Securite medicale",
    desc: "Aucun diagnostic. Uniquement une estimation du risque et des recommandations.",
  },
  {
    icon: Lock,
    title: "Donnees protegees",
    desc: "Vos informations sont chiffrees et traitees avec la plus grande confidentialite.",
  },
  {
    icon: Stethoscope,
    title: "Orientation professionnelle",
    desc: "Mise en relation avec des specialistes proches de chez vous.",
  },
];

export function TrustSection() {
  return (
    <section className="px-4 py-20">
      <div className="mx-auto max-w-4xl">
        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="mb-3 text-2xl font-bold text-gray-900 md:text-3xl">
            Concu avec rigueur et bienveillance
          </h2>
          <p className="text-gray-500">
            Un outil fiable, securise et medicalement responsable.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              className="flex gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-teal-50 text-teal-500">
                <f.icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="mb-1 font-semibold text-gray-900">{f.title}</h3>
                <p className="text-sm leading-relaxed text-gray-500">
                  {f.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
