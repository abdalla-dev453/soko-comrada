import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogIn } from "lucide-react";

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
        description="Log in to Comrade Plug to post gigs, apply for work, and manage your campus hustles."
        path="/login"
      />
      <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show">
          <h1 className="font-display font-semibold text-fluid-2xl">Welcome back</h1>
          <p className="mt-2 text-fluid-sm text-ink-muted">
            Log in with the student email you registered with.
          </p>

          <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-4">
            {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

            <div>
              <label htmlFor="email" className="text-fluid-sm font-medium text-ink">
                Student email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={form.email}
                onChange={set("email")}
                className={`${fieldClasses(Boolean(fieldErrors.email))} mt-1`}
                aria-invalid={Boolean(fieldErrors.email)}
              />
              <FieldError message={fieldErrors.email} />
            </div>

            <div>
              <label htmlFor="password" className="text-fluid-sm font-medium text-ink">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={form.password}
                onChange={set("password")}
                className={`${fieldClasses(Boolean(fieldErrors.password))} mt-1`}
                aria-invalid={Boolean(fieldErrors.password)}
              />
              <FieldError message={fieldErrors.password} />
            </div>

            <Button type="submit" icon={LogIn} loading={submitting} fullWidth>
              Log in
            </Button>
          </form>

          <p className="mt-6 text-fluid-sm text-ink-muted text-center">
            New to Soko Comrada?{" "}
            <Link to="/register" className="text-ink underline decoration-dotted">
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </>
  );
}