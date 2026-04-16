"use client";

import { motion } from "framer-motion";
import type { Question } from "@/types";

interface QuestionCardProps {
  question: Question;
  selectedOptionId: number | null;
  onSelect: (optionId: number, value: string) => void;
}

export function QuestionCard({
  question,
  selectedOptionId,
  onSelect,
}: QuestionCardProps) {
  return (
    <motion.div
      key={question.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.35 }}
      className="mx-auto w-full max-w-xl"
    >
      <div className="mb-3 inline-block rounded-full bg-sky-50 px-3 py-1 text-xs font-medium text-sky-600">
        {question.domain === "communication"
          ? "Communication"
          : question.domain === "social_interaction"
            ? "Interaction sociale"
            : question.domain === "behavior"
              ? "Comportements"
              : question.domain === "sensory"
                ? "Sensoriel"
                : question.domain}
      </div>

      <h2 className="mb-8 text-xl font-semibold leading-relaxed text-gray-900 md:text-2xl">
        {question.text}
      </h2>

      {question.description && (
        <p className="mb-6 text-sm text-gray-500">{question.description}</p>
      )}

      <div className="space-y-3">
        {question.options.map((option) => (
          <motion.button
            key={option.id}
            type="button"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => onSelect(option.id, option.value)}
            className={`w-full rounded-2xl border-2 px-6 py-4 text-left text-base font-medium transition-all ${
              selectedOptionId === option.id
                ? "border-sky-400 bg-sky-50 text-sky-700 shadow-sm"
                : "border-gray-100 bg-white text-gray-700 hover:border-gray-200 hover:bg-gray-50"
            }`}
          >
            {option.label}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
