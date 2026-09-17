import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { UserPlus } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { ErrorBanner, FieldError, fieldClasses } from "../components/common/ErrorBanner";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { heroItem } from "../utils/motion";

const initialForm = {
  name: "",
  email: "",
  password: "",
  phone_number: "",
  university: "",
  campus_location: "",
  referral_code: "",
};

export default function Register() {
  const { register } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState(initialForm);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    const errors = {};
    if (form.name.trim().length < 2) errors.name = "Enter your full name.";
    if (!/^\S+@\S+\.\S+$/.test(form.email)) errors.email = "Enter a valid email address.";
    if (form.password.length < 12) {
      errors.password = "Use at least 12 characters.";
    } else if (!/[A-Za-z]/.test(form.password) || !/\d/.test(form.password)) {
      errors.password = "Include at least one letter and one number.";
    }
    if (!/^\+?\d{9,15}$/.test(form.phone_number.trim()))
      errors.phone_number = "Enter a valid phone number, e.g. +254712345678.";
    if (!form.university.trim()) errors.university = "Enter your university.";
    if (!form.campus_location.trim()) errors.campus_location = "Enter your campus, e.g. JKUAT Juja.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;

    setSubmitting(true);
    try {
      await register({ ...form, name: form.name.trim(), email: form.email.trim().toLowerCase() });
      toast({ variant: "success", title: "You're in", description: "Welcome to Soko Comrada." });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      if (err.details && typeof err.details === "object") {
        setFieldErrors((existing) => ({ ...existing, ...Object.fromEntries(
          Object.entries(err.details).map(([field, messages]) => [
            field,
            Array.isArray(messages) ? messages.join(" ") : String(messages),
          ])
        ) }));
      }
      setFormError(
        err.message ||
          "Couldn't create your account. Make sure you're using a recognized student email."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title="Create your account"
        description="Register with your student email to post gigs and apply for campus work on Soko Comrada."
        path="/register"
      />
      <div className="mx-auto flex max-w-md flex-col justify-center px-4 py-16 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show">
          <h1 className="font-display font-semibold text-fluid-2xl">Join your campus market</h1>
          <p className="mt-2 text-fluid-sm text-ink-muted">
            Registration requires a recognized student email — it's how everyone else on
            the platform knows you're really a student here.
          </p>

          <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-4">
            {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

            <Field label="Full name" id="name" error={fieldErrors.name}>
              <input
                id="name"
                autoComplete="name"
                value={form.name}
                onChange={set("name")}
                className={fieldClasses(Boolean(fieldErrors.name))}
              />
            </Field>

            <Field label="Student email" id="email" error={fieldErrors.email}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@jkuat.ac.ke"
                value={form.email}
                onChange={set("email")}
                className={fieldClasses(Boolean(fieldErrors.email))}
              />
            </Field>

            <Field label="Password" id="password" error={fieldErrors.password}>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                value={form.password}
                onChange={set("password")}
                className={fieldClasses(Boolean(fieldErrors.password))}
              />
            </Field>

            <Field label="Phone number" id="phone_number" error={fieldErrors.phone_number}>
              <input
                id="phone_number"
                type="tel"
                autoComplete="tel"
                placeholder="+254712345678"
                value={form.phone_number}
                onChange={set("phone_number")}
                className={fieldClasses(Boolean(fieldErrors.phone_number))}
              />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="University" id="university" error={fieldErrors.university}>
                <input
                  id="university"
                  placeholder="JKUAT"
                  value={form.university}
                  onChange={set("university")}
                  className={fieldClasses(Boolean(fieldErrors.university))}
                />
              </Field>
              <Field label="Campus" id="campus_location" error={fieldErrors.campus_location}>
                <input
                  id="campus_location"
                  placeholder="JKUAT Juja"
                  value={form.campus_location}
                  onChange={set("campus_location")}
                  className={fieldClasses(Boolean(fieldErrors.campus_location))}
                />
              </Field>
            </div>

            <Button type="submit" icon={UserPlus} loading={submitting} fullWidth>
              Create account
            </Button>

            <div>
              <label htmlFor="referral_code" className="text-fluid-sm font-medium text-ink">
                Referral code <span className="text-ink-muted font-normal">(optional)</span>
              </label>
              <input
                id="referral_code"
                placeholder="e.g. AB1CD2E"
                value={form.referral_code}
                onChange={set("referral_code")}
                className={`${fieldClasses(false)} mt-1 uppercase tracking-wider`}
              />
              <p className="mt-1 text-fluid-xs text-ink-muted">
                Have a code from a classmate? They'll earn a free boost for referring you.
              </p>
            </div>
          </form>

          <p className="mt-6 text-fluid-sm text-ink-muted text-center">
            Already have an account?{" "}
            <Link to="/login" className="text-ink underline decoration-dotted">
              Log in
            </Link>
          </p>
        </motion.div>
      </div>
    </>
  );
}

function Field({ label, id, error, children }) {
  return (
    <div>
      <label htmlFor={id} className="text-fluid-sm font-medium text-ink">
        {label}
      </label>
      <div className="mt-1">{children}</div>
      <FieldError message={error} />
    </div>
  );
}
