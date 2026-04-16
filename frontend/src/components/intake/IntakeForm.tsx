"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ArrowLeft, User, Baby, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { SectionCard } from "@/components/shared/SectionCard";
import { CONCERN_OPTIONS } from "@/lib/concerns";
import { api } from "@/lib/api";

const schema = z.object({
  parent_name: z.string().min(2, "Nom requis"),
  email: z.string().email("Email invalide"),
  phone: z.string().optional(),
  child_first_name: z.string().min(1, "Prenom requis"),
  child_age: z.number().min(1, "Age requis").max(144, "Age maximum: 12 ans (144 mois)"),
  age_unit: z.enum(["months", "years"]),
  child_sex: z.enum(["M", "F"], { message: "Requis" }),
  respondent_role: z.string().min(1, "Requis"),
  city: z.string().min(1, "Ville requise"),
  postal_code: z.string().min(4, "Code postal requis"),
  address: z.string().optional(),
  concerns: z.array(z.string()).min(1, "Selectionnez au moins une preoccupation"),
  notes: z.string().optional(),
  consent: z.literal(true, { message: "Vous devez accepter les conditions" }),
});

type FormData = z.infer<typeof schema>;

const STEPS = [
  { id: 0, label: "Parent", icon: User },
  { id: 1, label: "Enfant", icon: Baby },
  { id: 2, label: "Preoccupations", icon: MessageSquare },
];

export function IntakeForm() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    trigger,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      age_unit: "months",
      child_age: undefined as unknown as number,
      concerns: [],
      consent: false as unknown as true,
    },
  });

  const concerns = watch("concerns");

  const toggleConcern = (value: string) => {
    const current = concerns || [];
    const next = current.includes(value)
      ? current.filter((c) => c !== value)
      : [...current, value];
    setValue("concerns", next, { shouldValidate: true });
  };

  const nextStep = async () => {
    const fieldsPerStep: (keyof FormData)[][] = [
      ["parent_name", "email"],
      ["child_first_name", "child_age", "child_sex", "respondent_role", "city", "postal_code"],
      ["concerns", "consent"],
    ];
    const valid = await trigger(fieldsPerStep[step]);
    if (valid) setStep((s) => Math.min(s + 1, 2));
  };

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError("");
    try {
      const ageMonths =
        data.age_unit === "years" ? data.child_age * 12 : data.child_age;

      const session = await api.createSession({
        parent_name: data.parent_name,
        child_first_name: data.child_first_name,
        child_age_months: ageMonths,
        child_sex: data.child_sex,
        respondent_role: data.respondent_role,
        main_concerns: data.concerns,
        city: data.city,
        postal_code: data.postal_code,
        address: data.address || "",
      });

      router.push(`/questionnaire?session=${session.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Une erreur est survenue");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      {/* Stepper */}
      <div className="mb-8 flex items-center justify-center gap-2">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${
                i === step
                  ? "bg-sky-100 text-sky-700"
                  : i < step
                    ? "bg-teal-50 text-teal-600 hover:bg-teal-100"
                    : "bg-gray-50 text-gray-400"
              }`}
            >
              <s.icon className="h-4 w-4" />
              <span className="hidden sm:inline">{s.label}</span>
            </button>
            {i < STEPS.length - 1 && (
              <div
                className={`h-px w-8 ${i < step ? "bg-teal-300" : "bg-gray-200"}`}
              />
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.3 }}
          >
            {/* Step 0: Parent */}
            {step === 0 && (
              <SectionCard>
                <h2 className="mb-6 text-xl font-semibold text-gray-900">
                  Informations du parent
                </h2>
                <div className="space-y-5">
                  <div>
                    <Label htmlFor="parent_name">Nom complet *</Label>
                    <Input
                      id="parent_name"
                      placeholder="Marie Dupont"
                      className="mt-1.5 h-12 rounded-xl"
                      {...register("parent_name")}
                    />
                    {errors.parent_name && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.parent_name.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="marie@exemple.fr"
                      className="mt-1.5 h-12 rounded-xl"
                      {...register("email")}
                    />
                    {errors.email && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.email.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="phone">Telephone (optionnel)</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="06 12 34 56 78"
                      className="mt-1.5 h-12 rounded-xl"
                      {...register("phone")}
                    />
                  </div>
                </div>
              </SectionCard>
            )}

            {/* Step 1: Child */}
            {step === 1 && (
              <SectionCard>
                <h2 className="mb-6 text-xl font-semibold text-gray-900">
                  Informations de l&apos;enfant
                </h2>
                <div className="space-y-5">
                  <div>
                    <Label htmlFor="child_first_name">Prenom *</Label>
                    <Input
                      id="child_first_name"
                      placeholder="Lucas"
                      className="mt-1.5 h-12 rounded-xl"
                      {...register("child_first_name")}
                    />
                    {errors.child_first_name && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.child_first_name.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="child_age">Age *</Label>
                      <Input
                        id="child_age"
                        type="number"
                        min={1}
                        placeholder="24"
                        className="mt-1.5 h-12 rounded-xl"
                        {...register("child_age", { valueAsNumber: true })}
                      />
                      {errors.child_age && (
                        <p className="mt-1 text-sm text-red-500">
                          {errors.child_age.message}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label>Unite</Label>
                      <div className="mt-1.5 flex gap-2">
                        {(["months", "years"] as const).map((u) => (
                          <button
                            key={u}
                            type="button"
                            onClick={() => setValue("age_unit", u)}
                            className={`flex-1 rounded-xl border px-4 py-3 text-sm font-medium transition-all ${
                              watch("age_unit") === u
                                ? "border-sky-300 bg-sky-50 text-sky-700"
                                : "border-gray-200 text-gray-500 hover:border-gray-300"
                            }`}
                          >
                            {u === "months" ? "Mois" : "Annees"}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label>Sexe *</Label>
                    <div className="mt-1.5 flex gap-3">
                      {[
                        { v: "M" as const, l: "Garcon" },
                        { v: "F" as const, l: "Fille" },
                      ].map((o) => (
                        <button
                          key={o.v}
                          type="button"
                          onClick={() => setValue("child_sex", o.v, { shouldValidate: true })}
                          className={`flex-1 rounded-xl border px-4 py-3 text-sm font-medium transition-all ${
                            watch("child_sex") === o.v
                              ? "border-sky-300 bg-sky-50 text-sky-700"
                              : "border-gray-200 text-gray-500 hover:border-gray-300"
                          }`}
                        >
                          {o.l}
                        </button>
                      ))}
                    </div>
                    {errors.child_sex && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.child_sex.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label>Vous etes *</Label>
                    <div className="mt-1.5 grid grid-cols-2 gap-2">
                      {[
                        { v: "mother", l: "La mere" },
                        { v: "father", l: "Le pere" },
                        { v: "guardian", l: "Tuteur/tutrice" },
                        { v: "other", l: "Autre" },
                      ].map((o) => (
                        <button
                          key={o.v}
                          type="button"
                          onClick={() =>
                            setValue("respondent_role", o.v, { shouldValidate: true })
                          }
                          className={`rounded-xl border px-4 py-3 text-sm font-medium transition-all ${
                            watch("respondent_role") === o.v
                              ? "border-sky-300 bg-sky-50 text-sky-700"
                              : "border-gray-200 text-gray-500 hover:border-gray-300"
                          }`}
                        >
                          {o.l}
                        </button>
                      ))}
                    </div>
                    {errors.respondent_role && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.respondent_role.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="city">Ville *</Label>
                      <Input
                        id="city"
                        placeholder="Paris"
                        className="mt-1.5 h-12 rounded-xl"
                        {...register("city")}
                      />
                      {errors.city && (
                        <p className="mt-1 text-sm text-red-500">
                          {errors.city.message}
                        </p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="postal_code">Code postal *</Label>
                      <Input
                        id="postal_code"
                        placeholder="75002"
                        className="mt-1.5 h-12 rounded-xl"
                        {...register("postal_code")}
                      />
                      {errors.postal_code && (
                        <p className="mt-1 text-sm text-red-500">
                          {errors.postal_code.message}
                        </p>
                      )}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="address">Adresse (optionnel)</Label>
                    <Input
                      id="address"
                      placeholder="15 rue de la Paix"
                      className="mt-1.5 h-12 rounded-xl"
                      {...register("address")}
                    />
                  </div>
                </div>
              </SectionCard>
            )}

            {/* Step 2: Concerns */}
            {step === 2 && (
              <SectionCard>
                <h2 className="mb-2 text-xl font-semibold text-gray-900">
                  Vos preoccupations
                </h2>
                <p className="mb-6 text-sm text-gray-500">
                  Selectionnez les elements qui vous preoccupent concernant le
                  developpement de votre enfant.
                </p>

                <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {CONCERN_OPTIONS.map((c) => (
                    <button
                      key={c.value}
                      type="button"
                      onClick={() => toggleConcern(c.value)}
                      className={`rounded-xl border px-4 py-3.5 text-left text-sm font-medium transition-all ${
                        concerns?.includes(c.value)
                          ? "border-sky-300 bg-sky-50 text-sky-700 shadow-sm"
                          : "border-gray-200 text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
                {errors.concerns && (
                  <p className="mb-4 text-sm text-red-500">
                    {errors.concerns.message}
                  </p>
                )}

                <div className="mb-6">
                  <Label htmlFor="notes">Notes supplementaires (optionnel)</Label>
                  <Textarea
                    id="notes"
                    placeholder="Decrivez toute observation supplementaire..."
                    className="mt-1.5 min-h-[100px] rounded-xl"
                    {...register("notes")}
                  />
                </div>

                <div className="flex items-start gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                  <Checkbox
                    id="consent"
                    checked={watch("consent") === true}
                    onCheckedChange={(checked) =>
                      setValue("consent", checked === true ? true : (false as unknown as true), {
                        shouldValidate: true,
                      })
                    }
                    className="mt-0.5"
                  />
                  <label htmlFor="consent" className="text-sm leading-relaxed text-gray-600">
                    J&apos;accepte que mes donnees soient utilisees dans le cadre de ce
                    pre-depistage. Je comprends que ce service ne constitue pas un
                    diagnostic medical.
                  </label>
                </div>
                {errors.consent && (
                  <p className="mt-2 text-sm text-red-500">
                    {errors.consent.message}
                  </p>
                )}
              </SectionCard>
            )}
          </motion.div>
        </AnimatePresence>

        {error && (
          <p className="mt-4 text-center text-sm text-red-500">{error}</p>
        )}

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={() => setStep((s) => Math.max(s - 1, 0))}
            disabled={step === 0}
            className="rounded-xl"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Precedent
          </Button>

          {step < 2 ? (
            <Button
              type="button"
              onClick={nextStep}
              className="rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 px-6"
            >
              Suivant
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 px-6"
            >
              {loading ? "Envoi..." : "Commencer le questionnaire"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
