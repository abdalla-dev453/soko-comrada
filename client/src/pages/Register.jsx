import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { UserPlus, Sparkles, ShieldCheck, TrendingUp, CheckCircle2 } from "lucide-react";

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
    if (form.password.length < 8) errors.password = "Use at least 8 characters.";
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

      <div className="min-h-screen w-full lg:grid lg:grid-cols-12 bg-surface">
        {/* LEFT / SIDE BANNER (Hidden on small screens, takes 5 cols on lg, 6 cols on xl) */}
        <div className="relative hidden lg:flex lg:col-span-5 xl:col-span-6 flex-col justify-between overflow-hidden p-10 text-white">
          {/* Background Image with Overlay */}
          <div className="absolute inset-0 z-0">
            <img
              src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=1600&auto=format&fit=crop"
              alt="Kenyan Students & Entrepreneurs"
              className="h-full w-full object-cover object-center transform scale-105 transition-transform duration-1000 hover:scale-100"
            />
            {/* Elegant Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-black/30" />
            <div className="absolute inset-0 bg-primary/20 mix-blend-overlay" />
          </div>

          {/* Top Brand Tag */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 backdrop-blur-md border border-white/20">
              <Sparkles className="h-4 w-4 text-emerald-400" />
              <span className="text-xs font-semibold tracking-wider uppercase">
                Comrade Plug Marketplace
              </span>
            </div>
          </div>

          {/* Center Content / Hero Pitch */}
          <div className="relative z-10 my-auto max-w-lg space-y-6 py-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="font-display text-4xl font-extrabold leading-tight tracking-tight text-white xl:text-5xl">
                Monetize your skills right on campus.
              </h2>
              <p className="mt-4 text-lg text-white/80 leading-relaxed">
                Connect with thousands of fellow comrades. Offer services, acquire side hustles, and grow your campus business in a trusted student ecosystem.
              </p>
            </motion.div>

            {/* Feature Highlights */}
            <motion.ul
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="space-y-3 pt-2"
            >
              {[
                "100% Student-verified network",
                "Instant payouts & secure gig tracking",
                "Exclusive to Kenyan Universities",
              ].map((text, idx) => (
                <li key={idx} className="flex items-center gap-3 text-sm font-medium text-white/90">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  {text}
                </li>
              ))}
            </motion.ul>

            {/* Social Proof Floating Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-8 rounded-2xl bg-white/10 p-4 backdrop-blur-md border border-white/15 shadow-2xl"
            >
              <div className="flex items-center gap-4">
                <div className="flex -space-x-2">
                  <span className="inline-block h-9 w-9 rounded-full ring-2 ring-white/50 bg-amber-500 text-xs font-bold text-white flex items-center justify-center">JKUAT</span>
                  <span className="inline-block h-9 w-9 rounded-full ring-2 ring-white/50 bg-blue-600 text-xs font-bold text-white flex items-center justify-center">UoN</span>
                  <span className="inline-block h-9 w-9 rounded-full ring-2 ring-white/50 bg-purple-600 text-xs font-bold text-white flex items-center justify-center">MUT</span>
                </div>
                <div>
                  <p className="text-xs font-bold text-white">Join 5,000+ Comrades</p>
                  <p className="text-xs text-white/70">Actively trading skills & services today</p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Bottom Footer note */}
          <div className="relative z-10 flex items-center gap-2 text-xs text-white/60">
            <ShieldCheck className="h-4 w-4" />
            <span>Strictly verified student-only marketplace</span>
          </div>
        </div>

        {/* RIGHT / FORM SECTION */}
        <div className="flex flex-col justify-center px-4 py-12 sm:px-8 lg:col-span-7 xl:col-span-6 lg:px-16 xl:px-24">
          <motion.div
            variants={heroItem}
            initial="hidden"
            animate="show"
            className="mx-auto w-full max-w-md"
          >
            {/* Header */}
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-surface-muted px-3 py-1 text-xs font-medium text-ink-muted border border-border/50 lg:hidden">
                <Sparkles className="h-3.5 w-3.5 text-emerald-500" />
                <span>Verified Comrade Network</span>
              </div>
              <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-ink">
                Join your campus market
              </h1>
              <p className="text-sm sm:text-base text-ink-muted leading-relaxed">
                Registration requires a recognized student email — it's how everyone else on the platform knows you're really a comrade.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
              {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

              <Field label="Full name" id="name" error={fieldErrors.name}>
                <input
                  id="name"
                  autoComplete="name"
                  placeholder="e.g. Brian Otieno"
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
                  placeholder="you@mut.ac.ke"
                  value={form.email}
                  onChange={set("email")}
                  className={fieldClasses(Boolean(fieldErrors.email))}
                />
              </Field>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="Password" id="password" error={fieldErrors.password}>
                  <input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="••••••••"
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
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="University" id="university" error={fieldErrors.university}>
                  <input
                    id="university"
                    placeholder="MUT"
                    value={form.university}
                    onChange={set("university")}
                    className={fieldClasses(Boolean(fieldErrors.university))}
                  />
                </Field>
                <Field label="Campus" id="campus_location" error={fieldErrors.campus_location}>
                  <input
                    id="campus_location"
                    placeholder="Murang'a Main Campus"
                    value={form.campus_location}
                    onChange={set("campus_location")}
                    className={fieldClasses(Boolean(fieldErrors.campus_location))}
                  />
                </Field>
              </div>

              <div className="pt-2">
                <Button 
                  type="submit" 
                  icon={UserPlus} 
                  loading={submitting} 
                  fullWidth
                  className="shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all py-3 text-base"
                >
                  Create account
                </Button>
              </div>
            </form>

            {/* Footer Links */}
            <p className="mt-8 text-center text-sm text-ink-muted">
              Already have an account?{" "}
              <Link 
                to="/login" 
                className="font-semibold text-ink underline underline-offset-4 decoration-primary/50 hover:decoration-primary transition-colors"
              >
                Log in
              </Link>
            </p>
          </motion.div>
        </div>
      </div>
    </>
  );
}

function Field({ label, id, error, children }) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-xs font-semibold uppercase tracking-wider text-ink/80">
        {label}
      </label>
      <div>{children}</div>
      <FieldError message={error} />
    </div>
  );
}