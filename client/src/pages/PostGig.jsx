import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Send, CheckCircle2, ShieldCheck, MapPin, DollarSign, Calendar, FileText } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { ErrorBanner, FieldError, fieldClasses } from "../components/common/ErrorBanner";
import { createGig } from "../api/gigs";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { heroItem } from "../utils/motion";

const CATEGORIES = [
  "gigs_work",
  "tutoring",
  "tech help",
  "design",
  "writing",
  "delivery",
  "photography",
  "errands",
  "events",
  "cleaning",
  "campus ambassador",
  "internship",
];

const OPPORTUNITY_TYPES = [
  { value: "GIG", label: "Quick Gig / Task" },
  { value: "PART_TIME", label: "Part-Time Job" },
  { value: "INTERNSHIP", label: "Internship" },
  { value: "ATTACHMENT", label: "Campus Attachment" },
  { value: "REMOTE_TASK", label: "Remote Freelance" },
];

const COMPENSATION_TYPES = [
  { value: "PAID", label: "Paid (Fixed / Stipend)" },
  { value: "NEGOTIABLE", label: "Negotiable" },
  { value: "UNPAID", label: "Volunteer / Club (Unpaid)" },
];

const WORK_ARRANGEMENTS = [
  { value: "ON_SITE", label: "On Campus / Physical" },
  { value: "REMOTE", label: "Fully Remote" },
  { value: "HYBRID", label: "Hybrid" },
];

const initialForm = {
  title: "",
  description: "",
  opportunity_type: "GIG",
  category: "gigs_work",
  work_arrangement: "ON_SITE",
  compensation_type: "PAID",
  budget: "",
  price_type: "FIXED",
  campus_location: "",
  hostel_location: "",
  landmark: "",
  skills_required: "",
  slots_needed: "1",
  is_urgent: false,
  deadline: "",
  deliverables: "",
  screening_question: "",
};

export default function PostGig() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [form, setForm] = useState(() => ({
    ...initialForm,
    campus_location: user?.campus_location || "",
  }));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const set = (key) => (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  const validateStep1 = () => {
    const errors = {};
    if (form.title.trim().length < 3) errors.title = "Give it a clear, specific title.";
    if (form.description.trim().length < 10) errors.description = "Provide at least a short description.";
    if (!form.category) errors.category = "Select a category.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateStep2 = () => {
    const errors = {};
    if (form.compensation_type === "PAID" && (!form.budget || Number(form.budget) <= 0)) {
      errors.budget = "Enter a valid budget in KES.";
    }
    if (!form.campus_location.trim()) errors.campus_location = "Enter your primary campus.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!validateStep1() || !validateStep2()) return;

    setSubmitting(true);
    try {
      const skillsArray = form.skills_required
        ? form.skills_required.split(",").map((s) => s.trim()).filter(Boolean)
        : [];

      const deliverablesArray = form.deliverables
        ? form.deliverables.split(",").map((d) => d.trim()).filter(Boolean)
        : [];

      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        opportunity_type: form.opportunity_type,
        category: form.category,
        work_arrangement: form.work_arrangement,
        compensation_type: form.compensation_type,
        budget: form.budget ? parseFloat(form.budget) : 0,
        price_type: form.price_type,
        campus_location: form.campus_location.trim(),
        landmark: [form.hostel_location.trim(), form.landmark.trim()].filter(Boolean).join(", ") || undefined,
        skills_required: skillsArray,
        is_urgent: form.is_urgent,
        slots_needed: parseInt(form.slots_needed, 10) || 1,
        deliverables: deliverablesArray,
      };

      if (form.deadline) payload.deadline = new Date(form.deadline).toISOString();

      const gig = await createGig(payload);
      toast({
        variant: "success",
        title: "Opportunity Published",
        description: gig.flagged_for_review
          ? "It is currently undergoing rapid safety verification before showing publicly."
          : "Your opportunity is live on Comrade Plug!",
      });
      navigate("/thank-you", { state: { gigId: gig.id, title: gig.title } });
    } catch (err) {
      setFormError(err.message || "Couldn't publish your opportunity. Please check details.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title="Post an Opportunity"
        description="Post a campus gig, internship, freelance task, or campus job for verified comrades."
        path="/gigs/new"
        noindex
      />
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show">
          {/* Header */}
          <div className="mb-8">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-accent bg-accent-soft px-2.5 py-1 rounded-full">
              <ShieldCheck className="h-3.5 w-3.5" /> Structured Opportunity Creator
            </span>
            <h1 className="mt-3 font-display font-semibold text-2xl sm:text-3xl">Post on Comrade Plug</h1>
            <p className="mt-1 text-sm text-ink-muted">
              Connect with verified university students for on-campus gigs, remote tasks, and internships.
            </p>
          </div>

          {/* Stepper Navigation */}
          <div className="flex items-center justify-between border-b border-border pb-4 mb-6 text-sm font-medium">
            <button
              type="button"
              onClick={() => setStep(1)}
              className={`flex items-center gap-2 pb-1 border-b-2 transition-colors ${
                step === 1 ? "border-accent text-accent font-semibold" : "border-transparent text-ink-muted hover:text-ink"
              }`}
            >
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-surface-raised border border-border text-xs">
                1
              </span>
              Opportunity Details
            </button>
            <button
              type="button"
              onClick={() => {
                if (validateStep1()) setStep(2);
              }}
              className={`flex items-center gap-2 pb-1 border-b-2 transition-colors ${
                step === 2 ? "border-accent text-accent font-semibold" : "border-transparent text-ink-muted hover:text-ink"
              }`}
            >
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-surface-raised border border-border text-xs">
                2
              </span>
              Budget, Location & Rules
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
            {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

            {step === 1 && (
              <div className="flex flex-col gap-4">
                <div>
                  <label htmlFor="title" className="text-sm font-medium text-ink flex items-center gap-1.5">
                    <FileText className="h-4 w-4 text-accent" /> Title
                  </label>
                  <input
                    id="title"
                    placeholder="e.g. Design flyers for Student Union Tech Week"
                    value={form.title}
                    onChange={set("title")}
                    className={`${fieldClasses(Boolean(fieldErrors.title))} mt-1`}
                  />
                  <FieldError message={fieldErrors.title} />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="opportunity_type" className="text-sm font-medium text-ink">
                      Opportunity Type
                    </label>
                    <select
                      id="opportunity_type"
                      value={form.opportunity_type}
                      onChange={set("opportunity_type")}
                      className={`${fieldClasses(false)} mt-1`}
                    >
                      {OPPORTUNITY_TYPES.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="category" className="text-sm font-medium text-ink">
                      Category
                    </label>
                    <select
                      id="category"
                      value={form.category}
                      onChange={set("category")}
                      className={`${fieldClasses(Boolean(fieldErrors.category))} mt-1`}
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c.replace("_", " ").toUpperCase()}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="description" className="text-sm font-medium text-ink">
                    Detailed Scope / Description
                  </label>
                  <textarea
                    id="description"
                    rows={4}
                    placeholder="Describe exactly what needs to be delivered, requirements, and background context."
                    value={form.description}
                    onChange={set("description")}
                    className={`${fieldClasses(Boolean(fieldErrors.description))} mt-1 resize-none`}
                  />
                  <FieldError message={fieldErrors.description} />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="work_arrangement" className="text-sm font-medium text-ink">
                      Work Mode
                    </label>
                    <select
                      id="work_arrangement"
                      value={form.work_arrangement}
                      onChange={set("work_arrangement")}
                      className={`${fieldClasses(false)} mt-1`}
                    >
                      {WORK_ARRANGEMENTS.map((w) => (
                        <option key={w.value} value={w.value}>
                          {w.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="skills_required" className="text-sm font-medium text-ink">
                      Skills Needed <span className="text-ink-muted font-normal">(comma-separated)</span>
                    </label>
                    <input
                      id="skills_required"
                      placeholder="e.g. Canva, Python, Photography"
                      value={form.skills_required}
                      onChange={set("skills_required")}
                      className={`${fieldClasses(false)} mt-1`}
                    />
                  </div>
                </div>

                <Button
                  type="button"
                  variant="primary"
                  className="mt-2"
                  onClick={() => {
                    if (validateStep1()) setStep(2);
                  }}
                >
                  Continue to Budget & Location →
                </Button>
              </div>
            )}

            {step === 2 && (
              <div className="flex flex-col gap-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label htmlFor="compensation_type" className="text-sm font-medium text-ink">
                      Payment Terms
                    </label>
                    <select
                      id="compensation_type"
                      value={form.compensation_type}
                      onChange={set("compensation_type")}
                      className={`${fieldClasses(false)} mt-1`}
                    >
                      {COMPENSATION_TYPES.map((c) => (
                        <option key={c.value} value={c.value}>
                          {c.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="budget" className="text-sm font-medium text-ink flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-success" /> Budget (KES)
                    </label>
                    <input
                      id="budget"
                      type="number"
                      min="0"
                      step="50"
                      placeholder="1500"
                      value={form.budget}
                      onChange={set("budget")}
                      disabled={form.compensation_type === "UNPAID"}
                      className={`${fieldClasses(Boolean(fieldErrors.budget))} mt-1`}
                    />
                    <FieldError message={fieldErrors.budget} />
                  </div>

                  <div>
                    <label htmlFor="price_type" className="text-sm font-medium text-ink">
                      Price Type
                    </label>
                    <select
                      id="price_type"
                      value={form.price_type}
                      onChange={set("price_type")}
                      disabled={form.compensation_type === "UNPAID"}
                      className={`${fieldClasses(false)} mt-1`}
                    >
                      <option value="FIXED">Fixed Price</option>
                      <option value="NEGOTIABLE">Negotiable</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="campus_location" className="text-sm font-medium text-ink flex items-center gap-1">
                      <MapPin className="h-4 w-4 text-accent" /> University / Campus
                    </label>
                    <input
                      id="campus_location"
                      placeholder="e.g. UoN Main Campus, Strathmore, JKUAT"
                      value={form.campus_location}
                      onChange={set("campus_location")}
                      className={`${fieldClasses(Boolean(fieldErrors.campus_location))} mt-1`}
                    />
                    <FieldError message={fieldErrors.campus_location} />
                  </div>

                  <div>
                    <label htmlFor="hostel_location" className="text-sm font-medium text-ink">
                      Hostel / Hall / Gate <span className="text-ink-muted font-normal">(optional)</span>
                    </label>
                    <input
                      id="hostel_location"
                      placeholder="e.g. Hall 4, Gate B, Lower Campus"
                      value={form.hostel_location}
                      onChange={set("hostel_location")}
                      className={`${fieldClasses(false)} mt-1`}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="deadline" className="text-sm font-medium text-ink flex items-center gap-1">
                      <Calendar className="h-4 w-4 text-warning" /> Deadline <span className="text-ink-muted font-normal">(optional)</span>
                    </label>
                    <input
                      id="deadline"
                      type="datetime-local"
                      value={form.deadline}
                      onChange={set("deadline")}
                      className={`${fieldClasses(false)} mt-1`}
                    />
                  </div>

                  <div>
                    <label htmlFor="slots_needed" className="text-sm font-medium text-ink">
                      Openings / Comrades Needed
                    </label>
                    <input
                      id="slots_needed"
                      type="number"
                      min="1"
                      max="50"
                      value={form.slots_needed}
                      onChange={set("slots_needed")}
                      className={`${fieldClasses(false)} mt-1`}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="deliverables" className="text-sm font-medium text-ink">
                    Expected Deliverables <span className="text-ink-muted font-normal">(comma-separated)</span>
                  </label>
                  <input
                    id="deliverables"
                    placeholder="e.g. Final .png flyer, High-res photos, Formatted PDF"
                    value={form.deliverables}
                    onChange={set("deliverables")}
                    className={`${fieldClasses(false)} mt-1`}
                  />
                </div>

                <div className="rounded-lg border border-border bg-surface-raised p-3.5">
                  <label className="flex items-center gap-2.5 text-sm text-ink cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={form.is_urgent}
                      onChange={set("is_urgent")}
                      className="h-4 w-4 rounded border-border text-accent focus:ring-accent/20"
                    />
                    <span className="font-medium text-warning">Flag as Urgent Priority (Needed within 24 hours)</span>
                  </label>
                </div>

                <div className="flex gap-3 mt-3">
                  <Button type="button" variant="secondary" onClick={() => setStep(1)}>
                    ← Back
                  </Button>
                  <Button type="submit" icon={Send} loading={submitting} className="flex-1">
                    Publish Opportunity Live
                  </Button>
                </div>
              </div>
            )}
          </form>
        </motion.div>
      </div>
    </>
  );
}
