# Comrade PLug — Post-MVP Roadmap

**Prepared as a follow-on to the PRD's Phase 1-4 build roadmap (§13).**
Phases 1-4 (config/DB, backend endpoints, frontend foundations, pages)
are built and verified — 17/17 backend tests passing, clean frontend
build. This roadmap covers what comes after the single-campus MVP
ships, ordered by what actually blocks adoption vs. what's a
nice-to-have.

Ordering principle: **fix trust and speed before adding features.**
A student who gets scammed once, or waits three hours for a boost to
go live, doesn't come back for the multi-person-gig feature.

---

## Roadmap at a glance

| # | Phase | Timeframe | Effort | Blocks on |
|---|---|---|---|---|
| 5 | Payment automation | Weeks 1-3 | ~8 dev-days | Daraja API sandbox access |
| 6 | Dispute resolution | Weeks 2-4 (parallel with 5) | ~6 dev-days | None — pure app-layer |
| 7 | WhatsApp notifications | Weeks 4-6 | ~5 dev-days | WhatsApp Business API approval (can take 1-2 weeks — apply Week 1) |
| 8 | Fulfillment precision | Weeks 6-8 | ~7 dev-days | Phase 6 (shares the Gig status model) |
| 9 | Trust & safety hardening | Weeks 7-9 (parallel with 8) | ~4 dev-days | None |
| 10 | Referral growth loop | Weeks 9-10 | ~3 dev-days | Phase 7 (WhatsApp share hooks) |

Total: **~33 dev-days** (roughly 7 weeks for one full-time engineer, less
with the two parallel tracks noted above) to go from "working MVP" to
"defensible against the WhatsApp-group status quo."

---

## Phase 5 — Payment automation (Daraja STK Push)

**Problem it solves:** manual M-Pesa verification caps you at however
many payments one admin can eyeball against a till statement per day.
Every hour of delay on a boost is an hour a genuinely urgent gig sits
buried in the feed — directly undercutting the "urgency isn't served
today" problem statement in PRD §2.

**What ships:**
- Replace the "submit a code, admin verifies" flow with Safaricom
  Daraja STK Push: student taps "Boost," gets a phone prompt, enters
  PIN, payment confirms via Daraja callback.
- `payment_service.py` already isolates this exact seam
  (`apply_verified_payment` / `verify_payment`) — Phase 4 was built
  with this swap in mind, so this is a new `daraja_service.py` plus a
  callback route (`POST /api/payments/daraja/callback`), not a
  rewrite of the payments blueprint.
- Keep manual verification as a fallback path for callback failures —
  don't rip it out, degrade to it.

**Effort:** ~8 dev-days (Daraja sandbox integration + callback
signature verification + retry/idempotency handling is the bulk of
it; the app-side plumbing is small because of how Phase 2 was
structured).

**Metrics — 30 days post-launch:**
- Median verification time: **from hours → under 60 seconds**
- **≥90%** of boost/subscription payments auto-verified with zero
  admin touch
- Admin manual-queue volume drops **≥80%** vs. current MVP baseline

---

## Phase 6 — Dispute resolution

**Problem it solves:** PRD §14 explicitly leaves this as an open
decision — "who resolves disputes when a gig is marked complete by
only one party." Right now a poster can mark complete and dodge
payment, or a hustler can claim completion falsely. This is the
single fastest way to burn the trust the whole platform is selling.

**What ships:**
- Two-sided completion: `POST /api/gigs/:id/complete` currently lets
  either party close a gig unilaterally. Add a `PENDING_CONFIRMATION`
  gig status — the second party has 48 hours to confirm or dispute
  before auto-completing.
- A `disputed` flag + reason on `Gig`, surfaced in the existing
  `Admin` page as a third tab (you already have the tab pattern from
  the payments/reports queues — this reuses it, doesn't invent a new
  UI paradigm).
- Simple mediation: admin sees both parties' account of what happened
  (reuse the existing report `reason` field), decides, closes.

**Effort:** ~6 dev-days (one new gig status, one migration, one
admin-panel tab, notification copy updates). No new external
dependency — this is the highest-leverage-per-dev-day item on this
whole roadmap.

**Metrics:**
- **<3%** of completed gigs disputed (matches your existing
  fulfillment-rate success metric in spirit)
- Median dispute resolution time: **<48 hours**
- Repeat-offender rate (same user disputed >1x): track it, no target
  yet — this becomes an input to a future trust-score feature

---

## Phase 7 — WhatsApp notifications

**Problem it solves:** the MVP's email fallback assumes students check
university email — most don't, regularly. WhatsApp open rates on this
demographic run 90%+ within minutes. This is a bigger adoption lever
than most in-app polish, because it meets students where they already
are (PRD §2's own diagnosis: the gig economy already runs on
WhatsApp).

**What ships:**
- WhatsApp Business API (Cloud API, not the old on-prem version) for
  the same "critical action" events `notification_service.py`
  already identifies: application accepted, gig completed, payment
  verified.
- This replaces the SMTP fallback for these three events; the
  computed-on-read in-app notification feed stays as-is.
- **Apply for WhatsApp Business API access in Week 1** — approval
  timelines are unpredictable and shouldn't gate the rest of this
  phase's engineering work.

**Effort:** ~5 dev-days engineering (template message approval + Meta's
review process is the long pole, not the code).

**Metrics:**
- Notification-to-action time (accepted application → applicant opens
  app) drops **3-5x** vs. current email-fallback baseline
- **≥70%** of critical notifications delivered via WhatsApp within 60
  seconds

---

## Phase 8 — Fulfillment precision

**Problem it solves:** two gaps in the current model that the real
informal economy doesn't have:

1. **Multi-person gigs.** "Need 4 people to help move" or "need 3 for
   event setup" doesn't fit one-accepted-applicant. Common in moving,
   event help, group tutoring — categories already in your MVP.
2. **Sub-campus location.** "JKUAT Juja" is a big area. "Near Gate B"
   vs. "Hostel 5" matters for anything requiring physical presence,
   which is most of your MVP categories.

**What ships:**
- `Gig.slots_needed` (int, default 1) + `Gig.slots_filled`. Accepting
  an applicant increments `slots_filled` instead of always flipping
  gig status to `IN_PROGRESS`; gig only closes to new applicants once
  slots are full. Applications/reviews already support multiple
  accepted applicants per gig at the data-model level (no schema
  redesign needed — `applications` already has no 1:1 constraint with
  gigs beyond one application per applicant).
- A free-text or landmark-tag field for sub-campus location, shown in
  the gig feed filter alongside the existing `campus_location` filter.

**Effort:** ~7 dev-days (one migration, feed/filter updates, applicant
UI changes to show "3 of 4 spots filled").

**Metrics:**
- Track **% of posted gigs requiring >1 person** in the first cohort —
  if meaningfully above 0%, this graduates from roadmap item to
  retention risk
- Median time from posting to first application should **drop** as
  location precision increases — worth A/B testing once there's real
  usage volume to compare against

---

## Phase 9 — Trust & safety hardening

**Problem it solves:** the "academic help" categories (tutoring,
proofreading) sit directly next to academic dishonesty — paying
someone to sit an exam, ghostwriting assignments. This doesn't scale
on manual admin review alone past a certain posting volume, and it's
a reputational risk that's cheap to mitigate early and expensive to
fix after an incident.

**What ships:**
- Keyword/category flagging on gig creation (server-side check in the
  existing `gigs` blueprint's create route) for high-risk phrases
  ("write my exam," "sit my test," "do my assignment for me") —
  routes to the admin reports queue for pre-publish review rather than
  auto-publishing.
- This is a rules-based filter, not ML — keep it simple and tune the
  keyword list from real flagged content in the first month.

**Effort:** ~4 dev-days.

**Metrics:**
- **100%** of flagged-category postings reviewed before going live
  (this one's a compliance floor, not an optimization target)
- False-positive rate on the keyword filter — track and tune, target
  **<15%** of flags being legitimate gigs

---

## Phase 10 — Referral growth loop

**Problem it solves:** campus economies spread through hostel blocks,
class WhatsApp groups, and hostel reps — a genuinely dense,
pre-existing network. Most consumer products don't get this kind of
free distribution channel; this one does, if you build for it
deliberately instead of leaving it to chance.

**What ships:**
- Simple referral mechanic: invite 3 classmates who complete
  registration → sender gets a free boost credit. Reuses the existing
  `Payment` model's purpose enum (add `REFERRAL_CREDIT` alongside
  `BOOST`/`SUBSCRIPTION`/`ESCROW`) rather than inventing a parallel
  credits system.
- Share flow rides on the WhatsApp integration from Phase 7 — send an
  invite link directly to a WhatsApp contact or group.

**Effort:** ~3 dev-days (small, because it's deliberately simple and
reuses existing payment/purpose infrastructure).

**Metrics:**
- K-factor (invites sent per user that convert to signups) — even
  **0.3-0.4** is a materially cheaper acquisition channel than paid
  ads for a single-campus pilot
- Cost per acquired user via referral vs. any paid channel you're
  running, tracked side by side

---

## Explicitly deferred (not because they're bad ideas — because they're not the bottleneck)

| Idea | Why it waits |
|---|---|
| In-app wallet / escrow balance | PRD §14 already flags this needs real Daraja B2C/C2B integration and has real legal/tax implications — Phase 4 (multi-campus scale) territory, not now |
| Gamified leaderboards / streaks | Doesn't address trust, speed, or payment friction — the three things actually blocking adoption right now |
| Portfolio / photo-upload for hustlers | Reasonable eventually; ships after ratings (already live) prove insufficient on their own |
| Cross-campus discovery | Explicit PRD Phase 4 item — needs the single-campus trust model validated first |

---

## What to watch across all of this

Two numbers from the original PRD's own success metrics (§4) will tell
you if this roadmap is working, more than any per-phase metric above:

- **Gig fulfillment rate** (applied → accepted → completed) — target
  was ≥60%. Phases 6 and 8 should move this up; Phase 5 should move it
  up by removing the boost-delay bottleneck.
- **Disputed/flagged transaction rate** — target was <2%. Phase 6 is
  built specifically to hit this; if it's not moving after Phase 6
  ships, that's a signal to revisit before building anything further
  down this list.