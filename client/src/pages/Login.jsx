import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogIn, Sparkles, ShieldCheck, Zap, Briefcase, Star } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { ErrorBanner, FieldError, fieldClasses } from "../components/common/ErrorBanner";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import { heroItem } from "../utils/motion";

export default function Login() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || "/dashboard";

  const [form, setForm] = useState({ email: "", password: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    const errors = {};
    if (!form.email.trim()) errors.email = "Enter your student email.";
    if (!form.password) errors.password = "Enter your password.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;

    setSubmitting(true);
    try {
      await login(form.email.trim(), form.password);
      toast({ variant: "success", title: "Welcome back" });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setFormError(err.message || "Couldn't log you in. Check your details and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title="Log in"
        description="Log in to ComradePlug to post gigs, apply for work, and manage your campus hustles."
        path="/login"
      />

      <div className="min-h-screen w-full lg:grid lg:grid-cols-12 bg-surface">
        {/* LEFT / SIDE BANNER */}
        <div className="relative hidden lg:flex lg:col-span-5 xl:col-span-6 flex-col justify-between overflow-hidden p-10 text-white">
          {/* Background Image with Overlay */}
          <div className="absolute inset-0 z-0">
            <img
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1600&auto=format&fit=crop"
              alt="Kenyan Students Collaborating"
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
                ComradePlug Marketplace
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
                Ready to secure your next campus gig?
              </h2>
              <p className="mt-4 text-lg text-white/80 leading-relaxed">
                Log back in to track your active orders, reply to buyers, and explore thousands of new opportunities posted today.
              </p>
            </motion.div>

            {/* Live Stats Glassmorphism Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="grid grid-cols-2 gap-4 pt-2"
            >
              <div className="rounded-xl bg-white/10 p-4 backdrop-blur-md border border-white/15">
                <div className="flex items-center gap-2 text-red-400 mb-1">
                  <Zap className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider">Fast Turnaround</span>
                </div>
                <p className="text-xl font-bold text-white">Same-Day</p>
                <p className="text-xs text-white/70">Campus Gig Deliveries</p>
              </div>

              <div className="rounded-xl bg-white/10 p-4 backdrop-blur-md border border-white/15">
                <div className="flex items-center gap-2 text-amber-400 mb-1">
                  <Star className="h-4 w-4 fill-amber-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider">Top Rated</span>
                </div>
                <p className="text-xl font-bold text-white">4.9 / 5.0</p>
                <p className="text-xs text-white/70">Comrade Trust Rating</p>
              </div>
            </motion.div>

            {/* Quick Teaser Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-6 rounded-2xl bg-white/10 p-4 backdrop-blur-md border border-white/15 shadow-2xl flex items-center gap-4"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <Briefcase className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">Active Gigs Waiting</p>
                <p className="text-xs text-white/70">Graphics, assignments, tech support, laundry & more</p>
              </div>
            </motion.div>
          </div>

          {/* Bottom Footer note */}
          <div className="relative z-10 flex items-center gap-2 text-xs text-white/60">
            <ShieldCheck className="h-4 w-4" />
            <span>Encrypted & secure student login</span>
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
                <Sparkles className="h-3.5 w-3.5 text-red-500" />
                <span>Verified Comrade Network</span>
              </div>
              <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-ink">
                Welcome back
              </h1>
              <p className="text-sm sm:text-base text-ink-muted leading-relaxed">
                Log in with the student email you registered with to manage your campus hustles.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-5">
              {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

              <div className="space-y-1.5">
                <label 
                  htmlFor="email" 
                  className="block text-xs font-semibold uppercase tracking-wider text-ink/80"
                >
                  Student email
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@jkuat.ac.ke"
                  value={form.email}
                  onChange={set("email")}
                  className={fieldClasses(Boolean(fieldErrors.email))}
                  aria-invalid={Boolean(fieldErrors.email)}
                />
                <FieldError message={fieldErrors.email} />
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label 
                    htmlFor="password" 
                    className="block text-xs font-semibold uppercase tracking-wider text-ink/80"
                  >
                    Password
                  </label>
                </div>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={set("password")}
                  className={fieldClasses(Boolean(fieldErrors.password))}
                  aria-invalid={Boolean(fieldErrors.password)}
                />
                <FieldError message={fieldErrors.password} />
              </div>

              <div className="pt-2">
                <Button 
                  type="submit" 
                  icon={LogIn} 
                  loading={submitting} 
                  fullWidth
                  className="shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all py-3 text-base"
                >
                  Log in
                </Button>
              </div>
            </form>

            {/* Footer Links */}
            <p className="mt-8 text-center text-sm text-ink-muted">
              New to ComradePlug?{" "}
              <Link 
                to="/register" 
                className="font-semibold text-ink underline underline-offset-4 decoration-primary/50 hover:decoration-primary transition-colors"
              >
                Create an account
              </Link>
            </p>
          </motion.div>
        </div>
      </div>
    </>
  );
}