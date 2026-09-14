import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Send } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { ErrorBanner, FieldError, fieldClasses } from "../components/common/ErrorBanner";
import { createGig } from "../api/gigs";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { heroItem } from "../utils/motion";

const CATEGORIES = [
  "gigs_work",
  "marketplace",
  "services",
];

const SUBCATEGORIES = {
  gigs_work: [
    "coding",
    "design",
    "assignment_help",
    "printing",
    "typing",
    "errands",
    "laundry",
  ],
  marketplace: [
    "electronics",
    "cookware",
    "hostel_items",
    "furniture",
  ],
  services: [
    "hairdressing",
    "barbering",
    "phone_repair",
    "laptop_repair",
    "photography",
    "catering",
  ],
};

const initialForm = {
  title: "",
  description: "",
  budget: "",
  price_type: "FIXED",
  gig_type: "TASK_NEEDED",
  category: "gigs_work",
  subcategory: "",
  campus_location: "",
  hostel_location: "",
  landmark: "",
  slots_needed: "1",
  is_urgent: false,
  deadline: "",
  deliverables: "",
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
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  const handleCategoryChange = (val) => {
    setForm((f) => ({ ...f, category: val, subcategory: "" }));
  };

  const validate = () => {
    const errors = {};
    if (form.title.trim().length < 3) errors.title = "Give it a clear, specific title.";
    if (form.description.trim().length < 10) errors.description = "Add a bit more detail.";
    if (!form.budget || Number(form.budget) <= 0) errors.budget = "Enter a budget in KES.";
    if (!form.campus_location.trim()) errors.campus_location = "Enter your campus.";
    if (form.deadline) {
      const d = new Date(form.deadline);
      if (isNaN(d.getTime())) errors.deadline = "Enter a valid date.";
    }
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
        landmark: form.landmark.trim() || undefined,
        hostel_location: form.hostel_location.trim() || undefined,
        slots_needed: parseInt(form.slots_needed, 10) || 1,
        deliverables: form.deliverables
          ? form.deliverables.split(",").map((d) => d.trim()).filter(Boolean)
          : [],
      });
      toast({
        variant: "success",
        title: "Gig submitted",
        description: gig.flagged_for_review
          ? "It's under a quick review before going live — usually a few hours."
          : "It's live on the feed now.",
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
          <h1 className="font-display font-semibold text-fluid-2xl">Post a gig</h1>
          <p className="mt-2 text-fluid-sm text-ink-muted">
            Be specific — a clear task with a fair budget gets picked up fastest.
          </p>

          <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-4">
            {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

            <div>
              <label htmlFor="title" className="text-fluid-sm font-medium text-ink">
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
              <label htmlFor="description" className="text-fluid-sm font-medium text-ink">
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
                <label htmlFor="budget" className="text-fluid-sm font-medium text-ink">
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
                <label htmlFor="price_type" className="text-fluid-sm font-medium text-ink">
                  Price type
                </label>
                <select
                  id="price_type"
                  value={form.price_type}
                  onChange={set("price_type")}
                  className={`${fieldClasses(false)} mt-1`}
                >
                  <option value="FIXED">Fixed price</option>
                  <option value="NEGOTIABLE">Negotiable</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="category" className="text-fluid-sm font-medium text-ink">
                  Category
                </label>
                <select
                  id="category"
                  value={form.category}
                  onChange={(e) => {
                    set("category")(e);
                    handleCategoryChange(e.target.value);
                  }}
                  className={`${fieldClasses(false)} mt-1`}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>

              {SUBCATEGORIES[form.category] && (
                <div>
                  <label htmlFor="subcategory" className="text-fluid-sm font-medium text-ink">
                    Sub-category
                  </label>
                  <select
                    id="subcategory"
                    value={form.subcategory}
                    onChange={set("subcategory")}
                    className={`${fieldClasses(false)} mt-1`}
                  >
                    <option value="">Any</option>
                    {SUBCATEGORIES[form.category].map((c) => (
                      <option key={c} value={c}>
                        {c.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="deadline" className="text-fluid-sm font-medium text-ink">
                Completion deadline <span className="text-ink-muted font-normal">(optional)</span>
              </label>
              <input
                id="deadline"
                type="datetime-local"
                value={form.deadline}
                onChange={set("deadline")}
                className={`${fieldClasses(Boolean(fieldErrors.deadline))} mt-1`}
              />
              {fieldErrors.deadline && (
                <p className="mt-1 text-fluid-xs text-coral">{fieldErrors.deadline}</p>
              )}
            </div>

            <div>
              <label htmlFor="deliverables" className="text-fluid-sm font-medium text-ink">
                Deliverables <span className="text-ink-muted font-normal">(comma-separated)</span>
              </label>
              <input
                id="deliverables"
                placeholder="e.g. Assignment typing, Poster design, Laundry"
                value={form.deliverables}
                onChange={set("deliverables")}
                className={fieldClasses(false)}
              />
              <p className="mt-1 text-fluid-xs text-ink-muted">
                What you'll receive when this is done.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="campus_location" className="text-fluid-sm font-medium text-ink">
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

              <div>
                <label htmlFor="hostel_location" className="text-fluid-sm font-medium text-ink">
                  Hostel / area <span className="text-ink-muted font-normal">(optional)</span>
                </label>
                <input
                  id="hostel_location"
                  placeholder="e.g. Lower Campus, Kiharu"
                  value={form.hostel_location}
                  onChange={set("hostel_location")}
                  className={fieldClasses(false)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="landmark" className="text-fluid-sm font-medium text-ink">
                  Nearest landmark <span className="text-ink-muted font-normal">(optional)</span>
                </label>
                <input
                  id="landmark"
                  placeholder="Near Gate B, Hostel 5…"
                  value={form.landmark}
                  onChange={set("landmark")}
                  className={`${fieldClasses(false)} mt-1`}
                />
                <p className="mt-1 text-fluid-xs text-ink-muted">
                  Helps applicants know where to find you.
                </p>
              </div>

              <div>
                <label htmlFor="slots_needed" className="text-fluid-sm font-medium text-ink">
                  People needed
                </label>
                <input
                  id="slots_needed"
                  type="number"
                  min="1"
                  max="20"
                  value={form.slots_needed}
                  onChange={set("slots_needed")}
                  className={`${fieldClasses(false)} mt-1`}
                />
                <p className="mt-1 text-fluid-xs text-ink-muted">
                  For moving, events, group help.
                </p>
              </div>
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
