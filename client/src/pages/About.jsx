import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { MapPinned, ShieldCheck, Users } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { heroContainer, heroItem } from "../utils/motion";

export default function About() {
  return (
    <>
      <SEO
        title="About"
        description="Why Soko Comrada exists: the campus gig economy already runs on WhatsApp — we're just making it safer and faster."
        path="/about"
      />

      <section className="relative isolate mx-auto max-w-3xl overflow-hidden rounded-b-card border-b border-border bg-gradient-to-br from-accent-soft to-surface-raised px-4 pt-16 pb-12 dark:from-accent-soft/20 sm:px-6">
        <div className="-z-1 absolute top-[-6rem] right-[-6rem] h-80 w-80 rounded-full bg-accent-soft blur-3xl" />
        <motion.div variants={heroContainer} initial="hidden" animate="show">
          <motion.h1 variants={heroItem} className="font-display font-bold text-3xl tracking-tight text-ink">
            Built by people who were tired of the group chat.
          </motion.h1>
          <motion.p variants={heroItem} className="mt-6 text-lg text-ink-muted leading-relaxed">
            Every campus already has an informal gig economy — someone who does hair
            braiding out of their room, someone who'll print your assignment at 11pm,
            someone who'll move your boxes for a few hundred bob. It just runs on
            scattered WhatsApp groups, word of mouth, and a fair amount of trust that
            occasionally gets burned.
          </motion.p>
          <motion.p variants={heroItem} className="mt-4 text-lg text-ink-muted leading-relaxed">
            ComradePlug doesn't invent that economy — it gives it a real address. One
            place, scoped to your own campus, where a task gets found in minutes instead
            of five group chats, and where a good track record actually follows you.
          </motion.p>
        </motion.div>
      </section>

      <section className="bg-surface-raised">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
          <div className="grid gap-10 sm:grid-cols-3">
            <Principle
              icon={MapPinned}
              title="Campus-first, always"
              body="You're not competing with the whole city — just people you'll actually run into between classes. That's what makes the trust model work."
            />
            <Principle
              icon={ShieldCheck}
              title="Verified, not anonymous"
              body="Registration is gated by student email. A rating that follows you means bad actors can't just make a new account and start over."
            />
            <Principle
              icon={Users}
              title="Built with one campus, for now"
              body="We're piloting on a single campus on purpose — get the trust and fulfillment mechanics right before spreading thin."
            />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16 sm:px-6 text-center">
        <h2 className="font-display font-semibold text-2xl">
          Got a task, or a skill worth listing?
        </h2>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Button as={Link} to="/register">
            Join free
          </Button>
          <Button as={Link} to="/contact" variant="secondary">
            Get in touch
          </Button>
        </div>
      </section>
    </>
  );
}

function Principle({ icon: Icon, title, body }) {
  return (
    <div className="card flex flex-col items-center gap-3 border border-border p-5 shadow-card">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
        <Icon className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="font-display font-semibold text-lg">{title}</h3>
      <p className="text-center text-sm text-ink-muted leading-relaxed">{body}</p>
    </div>
  );
}