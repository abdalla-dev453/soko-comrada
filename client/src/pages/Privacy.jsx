import { SEO } from "../components/common/SEO";

const SECTIONS = [
  {
    heading: "What we collect",
    body: `When you register, we collect your name, student email, phone number, university, and campus location — the minimum needed to verify you're a real student and to connect you with people on your own campus. When you post or apply to a gig, we store what you write in that listing or application. If you submit an M-Pesa code for a boost or subscription, we store the code and amount to verify the payment.`,
  },
  {
    heading: "How we use it",
    body: `Your profile information is used to show other students who they're dealing with — your name, campus, and rating are visible to anyone browsing gigs. Your email and phone number are never shown publicly; they're used for account verification and, for critical actions like an accepted application, an email notification. We do not sell your data to advertisers or third parties.`,
  },
  {
    heading: "Payment verification",
    body: `Boosts and entrepreneur subscriptions are verified manually against M-Pesa till statements in this pilot phase. We store the confirmation code you submit and its verification status. We do not store M-Pesa PINs, and we never ask for one.`,
  },
  {
    heading: "Cookies",
    body: `We use a small number of cookies and local-storage entries to keep you signed in and to remember your theme preference. We use lightweight, privacy-respecting analytics to understand which pages and features are actually used — see our cookie banner for the choice to accept or decline non-essential tracking.`,
  },
  {
    heading: "Your rights",
    body: `You can review and update your profile information at any time from your dashboard. To request deletion of your account and associated data, email us at hello@comradeplug.app — we'll confirm the request and process it within a reasonable timeframe, subject to records we're required to keep (e.g. completed payment records).`,
  },
  {
    heading: "Data retention",
    body: `We retain account and transaction data for as long as your account is active, and for a limited period after closure to resolve disputes, honor legal obligations, and maintain the integrity of the ratings system.`,
  },
  {
    heading: "Changes to this policy",
    body: `As Comrade Plug moves past the single-campus pilot, this policy will be updated to reflect new features (e.g. automated payment verification, push notifications). We'll post the effective date of any change at the top of this page.`,
  },
];

export default function Privacy() {
  return (
    <>
      <SEO
        title="Privacy policy"
        description="How Comrade Plug collects, uses, and protects your information."
        path="/privacy"
      />
      <div className="mx-auto max-w-2xl px-4 py-14 sm:px-6">
        <h1 className="font-display font-semibold text-fluid-2xl">Privacy policy</h1>
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