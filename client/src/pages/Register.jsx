import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, Shield, UserPlus } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { ErrorBanner, FieldError, fieldClasses } from "../components/common/ErrorBanner";
import * as authApi from "../api/auth";
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
  user_type: "student",
  business_name: "",
  business_registration_number: "",
  business_location: "",
  business_description: "",
  contact_person_name: "",
  contact_person_phone: "",
  contact_person_email: "",
};

export default function Register() {
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
    if (form.user_type === "student") {
      if (!form.university.trim()) errors.university = "Enter your university.";
      if (!form.campus_location.trim()) errors.campus_location = "Enter your campus, e.g. JKUAT Juja.";
    }
    if (form.user_type === "employer" && !form.business_name.trim()) errors.business_name = "Enter your business name.";
    if (form.user_type === "employer" && !form.business_registration_number.trim()) errors.business_registration_number = "Enter your registration number.";
    if (form.user_type === "employer" && !form.business_location.trim()) errors.business_location = "Enter your business location.";
    if (form.user_type === "employer" && !form.contact_person_name.trim()) errors.contact_person_name = "Enter the contact person's name.";
    if (form.user_type === "employer" && !/^\+?\d{9,15}$/.test(form.contact_person_phone.trim())) errors.contact_person_phone = "Enter a valid phone number.";
    if (form.user_type === "employer" && !/^\S+@\S+\.\S+$/.test(form.contact_person_email)) errors.contact_person_email = "Enter a valid email address.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;

    setSubmitting(true);
    try {
      if (form.user_type === "employer") {
        const payload = {
          name: form.name.trim(),
          email: form.email.trim().toLowerCase(),
          password: form.password,
          phone_number: form.phone_number,
          business_name: form.business_name.trim(),
          business_registration_number: form.business_registration_number.trim() || undefined,
          business_location: form.business_location.trim(),
          business_description: form.business_description.trim() || undefined,
          contact_person_name: form.contact_person_name.trim(),
          contact_person_phone: form.contact_person_phone,
          contact_person_email: form.contact_person_email.trim().toLowerCase(),
        };
        await authApi.registerEmployer(payload);
      } else {
        await authApi.registerStudent({ ...form, name: form.name.trim(), email: form.email.trim().toLowerCase() });
      }
      toast({ variant: "success", title: "You're in", description: "Welcome to CampusGig Kenya." });
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
        description="Register with your student email or employer business details to post opportunities and apply for campus work on CampusGig Kenya."
        path="/register"
      />
      <div className="mx-auto flex max-w-md flex-col justify-center px-4 py-16 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show">
          <h1 className="font-display font-semibold text-fluid-2xl">Join your campus market</h1>
          <p className="mt-2 text-fluid-sm text-text-secondary">
            {form.user_type === "employer"
              ? "Employers must verify their business email and registration. Once verified, you can post opportunities to Kenyan students."
              : 'Registration requires a recognized student email — it\'s how everyone else on the platform knows you\'re really a student here.'}
          </p>

          <div className="mt-6 flex items-center gap-2 rounded-lg bg-canvas p-1.5 text-sm">
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, user_type: "student" }))}
              className={`flex items-center gap-2 rounded-md px-3 py-2 font-medium transition-all ${
                form.user_type === "student"
                  ? "bg-brand-500 text-surface shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }}`}
            >
              <GraduationCap size={16} /> Student
            </button>
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, user_type: "employer" }))}
              className={`flex items-center gap-2 rounded-md px-3 py-2 font-medium transition-all ${
                form.user_type === "employer"
                  ? "bg-brand-500 text-surface shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }}`}
            >
              <Shield size={16} /> Employer
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate className="mt-8 flex flex-col gap-4">
            {formError && <ErrorBanner message={formError} onDismiss={() => setFormError("")} />}

            <Field label={form.user_type === "employer" ? "Full name" : "Full name"} id="name" error={fieldErrors.name}>
              <input
                id="name"
                autoComplete="name"
                value={form.name}
                onChange={set("name")}
                className={fieldClasses(Boolean(fieldErrors.name))}
              />
            </Field>

            <Field label={form.user_type === "employer" ? "Business email" : "Student email"} id="email" error={fieldErrors.email}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder={form.user_type === "employer" ? "you@company.com" : "you@jkuat.ac.ke"}
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

            {form.user_type === "student" && (
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
            )}

            <Button type="submit" icon={UserPlus} loading={submitting} fullWidth>
              Create account
            </Button>

            {form.user_type === "employer" && (
              <>
                <Field label="Business name" id="business_name" error={fieldErrors.business_name}>
                  <input
                    id="business_name"
                    placeholder="Acme Ltd."
                    value={form.business_name}
                    onChange={set("business_name")}
                    className={fieldClasses(Boolean(fieldErrors.business_name))}
                  />
                </Field>

                <Field label="Business registration number" id="business_registration_number" error={fieldErrors.business_registration_number}>
                  <input
                    id="business_registration_number"
                    placeholder="CR 12345"
                    value={form.business_registration_number}
                    onChange={set("business_registration_number")}
                    className={fieldClasses(Boolean(fieldErrors.business_registration_number))}
                  />
                </Field>

                <Field label="Business location" id="business_location" error={fieldErrors.business_location}>
                  <input
                    id="business_location"
                    placeholder="Nairobi, Kenya"
                    value={form.business_location}
                    onChange={set("business_location")}
                    className={fieldClasses(Boolean(fieldErrors.business_location))}
                  />
                </Field>

                <Field label="Contact person name" id="contact_person_name" error={fieldErrors.contact_person_name}>
                  <input
                    id="contact_person_name"
                    placeholder="Jane Doe"
                    value={form.contact_person_name}
                    onChange={set("contact_person_name")}
                    className={fieldClasses(Boolean(fieldErrors.contact_person_name))}
                  />
                </Field>

                <Field label="Contact person phone" id="contact_person_phone" error={fieldErrors.contact_person_phone}>
                  <input
                    id="contact_person_phone"
                    type="tel"
                    placeholder="+254712345678"
                    value={form.contact_person_phone}
                    onChange={set("contact_person_phone")}
                    className={fieldClasses(Boolean(fieldErrors.contact_person_phone))}
                  />
                </Field>

                <Field label="Contact person email" id="contact_person_email" error={fieldErrors.contact_person_email}>
                  <input
                    id="contact_person_email"
                    type="email"
                    placeholder="contact@company.com"
                    value={form.contact_person_email}
                    onChange={set("contact_person_email")}
                    className={fieldClasses(Boolean(fieldErrors.contact_person_email))}
                  />
                </Field>

                <Field label="Business description" id="business_description" error={fieldErrors.business_description}>
                  <textarea
                    id="business_description"
                    rows={3}
                    placeholder="Briefly describe what your business does..."
                    value={form.business_description}
                    onChange={set("business_description")}
                    className={`${fieldClasses(false)} mt-1 resize-none`}
                  />
                </Field>
              </>
            )}

            <div>
              <label htmlFor="referral_code" className="text-fluid-sm font-medium text-text-primary">
                Referral code <span className="text-text-secondary font-normal">(optional)</span>
              </label>
              <input
                id="referral_code"
                placeholder="e.g. AB1CD2E"
                value={form.referral_code}
                onChange={set("referral_code")}
                className={`${fieldClasses(false)} mt-1 uppercase tracking-wider`}
              />
              <p className="mt-1 text-fluid-xs text-text-secondary">
                Have a code from a classmate? They'll earn a free boost for referring you.
              </p>
            </div>
          </form>

          <p className="mt-6 text-fluid-sm text-text-secondary text-center">
            Already have an account?{" "}
            <Link to="/login" className="text-text-primary underline decoration-dotted">
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
      <label htmlFor={id} className="text-fluid-sm font-medium text-text-primary">{label}</label>
      <div className="mt-1">{children}</div>
      <FieldError message={error} />
    </div>
  );
}
