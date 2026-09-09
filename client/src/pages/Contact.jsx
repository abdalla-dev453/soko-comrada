import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, MapPin, Send } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { FieldError, fieldClasses } from "../components/common/ErrorBanner";
import { heroItem } from "../utils/motion";
import { trackEvent } from "../utils/analytics";

const CONTACT_EMAIL = "hello@comradeplug.app";

const initialForm = { name: "", email: "", message: "" };

export default function Contact() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    const next = {};
    if (form.name.trim().length < 2) next.name = "Enter your name.";
    if (!/^\S+@\S+\.\S+$/.test(form.email)) next.email = "Enter a valid email.";
    if (form.message.trim().length < 10) next.message = "Say a bit more — 10 characters minimum.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    trackEvent("contact_form_submit");

    // No backend /contact endpoint exists yet — this opens the
    // person's own mail client with the message prefilled, which
    // actually reaches CONTACT_EMAIL rather than faking a success
    // state against an endpoint that isn't there.
    const subject = encodeURIComponent(`Message from ${form.name} via ComradePlug`);
    const body = encodeURIComponent(`${form.message}\n\n— ${form.name} (${form.email})`);
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;

    navigate("/thank-you", { state: { context: "contact" } });
  };

  return (
    <>
      <SEO
        title="Contact"
        description="Reach the ComradePlug team — questions, partnership ideas, or a campus you'd like us to launch on next."
        path="/contact"
      />

      <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6">
        <motion.div variants={heroItem} initial="hidden" animate="show" className="grid gap-12 md:grid-cols-2">
          <div>
            <h1 className="font-display font-semibold text-fluid-2xl">Talk to us</h1>
            <p className="mt-3 text-fluid-sm text-ink-muted leading-relaxed">
              Question about how ComradePlug works, a trust & safety concern, or want us
              on your campus next? We read everything that comes through here.
            </p>

            <div className="mt-8 flex flex-col gap-4">
              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 flex-shrink-0 text-moss-strong mt-0.5" aria-hidden="true" />
                <div>
                  <p className="text-fluid-sm font-medium text-ink">Email</p>
                  <a href={`mailto:${CONTACT_EMAIL}`} className="text-fluid-sm text-ink-muted hover:text-ink">
                    {CONTACT_EMAIL}
                  </a>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 flex-shrink-0 text-moss-strong mt-0.5" aria-hidden="true" />
                <div>
                  <p className="text-fluid-sm font-medium text-ink">Pilot campus</p>
                  <p className="text-fluid-sm text-ink-muted">
                    MUT Campus, MURANG'A County, Kenya
                  </p>
                </div>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
            <div>
              <label htmlFor="contact-name" className="text-fluid-sm font-medium text-ink">
                Name
              </label>
              <input
                id="contact-name"
                value={form.name}
                onChange={set("name")}
                className={`${fieldClasses(Boolean(errors.name))} mt-1`}
                aria-invalid={Boolean(errors.name)}
              />
              <FieldError message={errors.name} />
            </div>

            <div>
              <label htmlFor="contact-email" className="text-fluid-sm font-medium text-ink">
                Email
              </label>
              <input
                id="contact-email"
                type="email"
                value={form.email}
                onChange={set("email")}
                className={`${fieldClasses(Boolean(errors.email))} mt-1`}
                aria-invalid={Boolean(errors.email)}
              />
              <FieldError message={errors.email} />
            </div>

            <div>
              <label htmlFor="contact-message" className="text-fluid-sm font-medium text-ink">
                Message
              </label>
              <textarea
                id="contact-message"
                rows={5}
                value={form.message}
                onChange={set("message")}
                className={`${fieldClasses(Boolean(errors.message))} mt-1 resize-none`}
                aria-invalid={Boolean(errors.message)}
              />
              <FieldError message={errors.message} />
            </div>

            <Button type="submit" icon={Send} fullWidth>
              Send message
            </Button>
            <p className="text-fluid-xs text-ink-muted">
              Opens your email app with this pre-filled, addressed to {CONTACT_EMAIL}.
            </p>
          </form>
        </motion.div>
      </div>
    </>
  );
}