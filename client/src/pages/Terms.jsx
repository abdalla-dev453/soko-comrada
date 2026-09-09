import { SEO } from "../components/common/SEO";

const SECTIONS = [
  {
    heading: "Who can use ComradePlug",
    body: `Registration is restricted to students with a recognized university email domain. You must provide accurate information when registering and keep your account details up to date. You're responsible for activity that happens under your account.`,
  },
  {
    heading: "Posting and applying to gigs",
    body: `A gig posting must accurately describe the task or skill on offer and its budget. We don't allow listings for illegal services, academic dishonesty (e.g. paying someone to sit an exam for you), or anything that violates university policy. Applying to a gig is not a binding contract until the poster accepts your application — either party can withdraw before that point.`,
  },
  {
    heading: "Payments and fees",
    body: `Boost and subscription fees are paid via M-Pesa to the till number shown at checkout and verified manually by our team in this pilot phase. ComradePlug does not currently hold funds in escrow for the underlying gig payment between poster and hustler — that transaction happens directly between the two of you, and you should agree on payment terms before work begins.`,
  },
  {
    heading: "Ratings and reviews",
    body: `Reviews must reflect a genuine completed gig between the reviewer and reviewee. Fake, retaliatory, or coordinated reviews may be removed, and repeat offenders may be suspended. Ratings are visible on public profiles and cannot be selectively hidden by the person being reviewed.`,
  },
  {
    heading: "Reporting and enforcement",
    body: `Use the in-app report feature for scams, no-shows, harassment, or other abuse. Our team reviews reports and may warn, suspend, or permanently remove accounts that violate these terms. We aim to review reports promptly but cannot guarantee a specific resolution time during the pilot.`,
  },
  {
    heading: "Limitation of liability",
    body: `ComradePlug is a platform that connects students; we are not a party to the agreements students make with each other and are not liable for the quality, safety, or legality of work performed, or for payment disputes between users. Use the platform's reporting tools if something goes wrong.`,
  },
  {
    heading: "Changes to these terms",
    body: `We may update these terms as the platform grows beyond the single-campus pilot. Material changes will be posted here with an updated effective date, and continued use of ComradePlug after a change constitutes acceptance of the new terms.`,
  },
];

export default function Terms() {
  return (
    <>
      <SEO
        title="Terms of service"
        description="The rules for posting gigs, applying to work, and using ComradePlug."
        path="/terms"
      />
      <div className="mx-auto max-w-2xl px-4 py-14 sm:px-6">
        <h1 className="font-display font-semibold text-fluid-2xl">Terms of service</h1>
        <p className="mt-2 text-fluid-sm text-ink-muted">
          Last updated September 2026 · Pilot version — this is a working template and
          should be reviewed by counsel before public launch.
        </p>

        <div className="mt-10 flex flex-col gap-8">
          {SECTIONS.map((section) => (
            <section key={section.heading}>
              <h2 className="font-display font-semibold text-fluid-lg mb-2">{section.heading}</h2>
              <p className="text-fluid-sm text-ink-muted leading-relaxed">{section.body}</p>
            </section>
          ))}
        </div>
      </div>
    </>
  );
}