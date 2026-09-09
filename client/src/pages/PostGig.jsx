import { motion } from "framer-motion";
import { Send } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createGig } from "../api/gigs";
import { Button } from "../components/common/Button";
import {
  ErrorBanner,
  FieldError,
  fieldClasses,
} from "../components/common/ErrorBanner";
import { SEO } from "../components/common/SEO";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { heroItem } from "../utils/motion";

const CATEGORIES = [
  "writing",
  "cleaning",
  "tech help",
  "tutoring",
  "printing",
  "beauty",
  "errands",
  "design",
  "photography",
  "moving help",
];

const initialForm = {
  title: "",
  description: "",
  budget: "",
  gig_type: "TASK_NEEDED",
  category: "writing",
  campus_location: "",
  is_urgent: false,
};

export default function PostGig() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState(() => ({
    ...initialForm,
    campus_location: user?.campus_location || "",
  }));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const set = (key) => (e) => {
    const value =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  const validate = () => {
    const errors = {};
    if (form.title.trim().length < 3)
      errors.title = "Give it a clear, specific title.";
    if (form.description.trim().length < 10)
      errors.description = "Add a bit more detail.";
    if (!form.budget || Number(form.budget) <= 0)
      errors.budget = "Enter a budget in KES.";
    if (!form.campus_location.trim())
      errors.campus_location = "Enter your campus.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;

    setSubmitting(true);
    try {
      const gig = await createGig({
        ...form,
        title: form.title.trim(),
        description: form.description.trim(),
        budget: form.budget,
      });
      toast({
        variant: "success",
        title: "Gig posted",
        description: "It's live on the feed now.",
      });
      navigate("/thank-you", { state: { gigId: gig.id, title: gig.title } });
    } catch (err) {
      setFormError(err.message || "Couldn't post your gig. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title="Post a gig"
        description="Describe the task or skill you need on your campus and get applicants within hours."
        path="/gigs/new"
        noindex
      />
      <div className="mx-auto max-w-xl px-4 py-12 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show">
          <h1 className="font-display font-semibold text-fluid-2xl">
            Post a gig
          </h1>
          <p className="mt-2 text-fluid-sm text-ink-muted">
            Be specific — a clear task with a fair budget gets picked up
            fastest.
          </p>

          <form
            onSubmit={handleSubmit}
            noValidate
            className="mt-8 flex flex-col gap-4"
          >
            {formError && (
              <ErrorBanner
                message={formError}
                onDismiss={() => setFormError("")}
              />
            )}

            <div>
              <label
                htmlFor="title"
                className="text-fluid-sm font-medium text-ink"
              >
                Title
              </label>
              <input
                id="title"
                placeholder="Format my essay to APA, 10 pages"
                value={form.title}
                onChange={set("title")}
                className={`${fieldClasses(Boolean(fieldErrors.title))} mt-1`}
              />
              <FieldError message={fieldErrors.title} />
            </div>

            <div>
              <label
                htmlFor="description"
                className="text-fluid-sm font-medium text-ink"
              >
                Description
              </label>
              <textarea
                id="description"
                rows={4}
                placeholder="What needs to happen, by when, and anything the applicant should know."
                value={form.description}
                onChange={set("description")}
                className={`${fieldClasses(Boolean(fieldErrors.description))} mt-1 resize-none`}
              />
              <FieldError message={fieldErrors.description} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label
                  htmlFor="budget"
                  className="text-fluid-sm font-medium text-ink"
                >
                  Budget (KES)
                </label>
                <input
                  id="budget"
                  type="number"
                  min="0"
                  step="1"
                  placeholder="500"
                  value={form.budget}
                  onChange={set("budget")}
                  className={`${fieldClasses(Boolean(fieldErrors.budget))} mt-1`}
                />
                <FieldError message={fieldErrors.budget} />
              </div>

              <div>
                <label
                  htmlFor="category"
                  className="text-fluid-sm font-medium text-ink"
                >
                  Category
                </label>
                <select
                  id="category"
                  value={form.category}
                  onChange={set("category")}
                  className={`${fieldClasses(false)} mt-1`}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c[0].toUpperCase() + c.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <span className="text-fluid-sm font-medium text-ink">Type</span>
              <div className="mt-1 grid grid-cols-2 gap-2">
                {[
                  { value: "TASK_NEEDED", label: "I need this done" },
                  { value: "SKILL_OFFERED", label: "I'm offering a skill" },
                ].map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center justify-center rounded-lg border px-3 py-2.5 text-fluid-sm cursor-pointer transition-colors ${
                      form.gig_type === opt.value
                        ? "border-moss bg-moss-soft text-moss-strong font-medium"
                        : "border-border text-ink-muted hover:border-ink/20"
                    }`}
                  >
                    <input
                      type="radio"
                      name="gig_type"
                      value={opt.value}
                      checked={form.gig_type === opt.value}
                      onChange={set("gig_type")}
                      className="sr-only"
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label
                htmlFor="campus_location"
                className="text-fluid-sm font-medium text-ink"
              >
                Campus
              </label>
              <input
                id="campus_location"
                placeholder="JKUAT Juja"
                value={form.campus_location}
                onChange={set("campus_location")}
                className={`${fieldClasses(Boolean(fieldErrors.campus_location))} mt-1`}
              />
              <FieldError message={fieldErrors.campus_location} />
            </div>

            <label className="flex items-center gap-2 text-fluid-sm text-ink cursor-pointer select-none">
              <input
                type="checkbox"
                checked={form.is_urgent}
                onChange={set("is_urgent")}
                className="h-4 w-4 rounded border-border text-coral focus:ring-coral/40"
              />
              This can't wait — flag it urgent
            </label>

            <Button type="submit" icon={Send} loading={submitting} fullWidth>
              Post gig
            </Button>
          </form>
        </motion.div>
      </div>
    </>
  );
}
