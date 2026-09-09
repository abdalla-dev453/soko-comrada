# Comrade Plug

Campus micro-gig & skill marketplace. Monorepo containing two
independently deployable projects:

```
soko-comrada-backend/    Flask API (Blueprints), MySQL via SQLAlchemy + Alembic
soko-comrada-frontend/   React (Vite) SPA, Tailwind CSS
```

## Quick start (local development)

### 1. Database

Create a local MySQL 8.x database and user matching your
`soko-comrada-backend/.env` values:

```sql
CREATE DATABASE soko_comrada CHARACTER SET utf8mb4;
CREATE USER 'soko_app'@'%' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON soko_comrada.* TO 'soko_app'@'%';
FLUSH PRIVILEGES;
```

### 2. Backend

```bash
cd soko-comrada-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit DB_* and SECRET_KEY/JWT_SECRET_KEY values
flask db upgrade        # applies migrations/versions/0001 and 0002
python run.py            # http://localhost:5000
```

To run the backend test suite instead (uses an in-memory SQLite DB,
no MySQL required):

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

### 3. Frontend

```bash
cd soko-comrada-frontend
npm install
cp .env.example .env
npm run dev               # http://localhost:5173
```

### 3. Frontend

```bash
cd soko-comrada-frontend
npm install
cp .env.example .env
npm run dev               # http://localhost:5173
```

To verify the production build (what actually ships):

```bash
npm run build              # outputs to dist/
npm run lint
npm run preview            # serves dist/ locally
```

## Project status

This scaffold is being built in phases against `Soko_Comrada_PRD.pdf`:

- [x] Phase 1 — Configuration & database core
- [x] Phase 2 — Backend endpoints & core logic
- [x] Phase 3 — Frontend foundations & state (Tailwind theme, API client, auth/theme/toast context, layout chrome)
- [x] Phase 4 — Feature components & page views (all 15 pages, gig/payment components)

Frontend build verified: `npm run build` and `npm run lint` both pass clean
against the actual dependency tree (not just reviewed by eye). Backend:
17/17 pytest passing.

Two small backend additions came out of building the frontend against
real endpoints rather than the API table in isolation — both are
additive, don't change any existing route, and are covered by tests:
- `GET /api/gigs/mine` — a poster's own gigs, mirroring the existing
  `GET /api/applications/mine`. The Dashboard page needs this and the
  original PRD API table didn't include it.
- `GET /api/reviews/user/<id>` now also returns `{"user": ...}` alongside
  `{"reviews": [...]}`, so the public profile page can show a name and
  rating instead of just an anonymous review list.

See each project's own structure for details; the database schema in
`soko-comrada-backend/migrations/versions/0001_initial_schema.py`
mirrors PRD §8 exactly, including the security corrections called out
in PRD §12 (parameterized queries via the ORM, bcrypt password
hashing, no hardcoded credentials). `0002_add_admin_flag.py` adds the
`is_admin` column Phase 2's admin-only endpoints need.

### Known gaps / follow-ups worth knowing about

- **`sitemap.xml` is static.** It covers the marketing pages (home,
  about, contact, privacy, terms) but can't list individual gigs — a
  Vite SPA has no server to generate XML per-request. Dynamic gig
  entries would need a small backend route (e.g.
  `GET /api/sitemap-gigs.xml`) once that matters for SEO.
- **The contact form has no backend endpoint.** It opens the visitor's
  email client via a `mailto:` link pre-filled with their message,
  addressed to `hello@sokocomrada.app`, rather than silently pretending
  to submit to an API that doesn't exist. Wire up a real
  `POST /api/contact` (and a matching blueprint) if you want submissions
  to land in a database/inbox instead.
- **Privacy policy and terms of service are template content** written
  for this pilot, not reviewed by a lawyer — flagged in-page. Get real
  legal review before public launch.
- **No escrow.** Payment between poster and hustler happens directly
  between the two of you (PRD §14 open decision, PRD roadmap Phase 4
  covers real Daraja B2C/C2B escrow later).

## Manual API verification (curl)

Backend must be running (`python run.py`) and a MySQL DB migrated,
or run the automated suite instead (`python -m pytest -q`, no MySQL
needed). Every request below was exercised against the automated
test suite, so this checklist doubles as the exact happy path it
covers.

```bash
BASE=http://localhost:5000/api

# 1. Register two students (poster + hustler)
curl -s -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
  "name": "Amina Wanjiru", "email": "amina@jkuat.ac.ke", "password": "supersecret123",
  "phone_number": "+254712345678", "university": "JKUAT", "campus_location": "JKUAT Juja"
}' | tee poster.json

curl -s -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
  "name": "Brian Otieno", "email": "brian@jkuat.ac.ke", "password": "supersecret123",
  "phone_number": "+254798765432", "university": "JKUAT", "campus_location": "JKUAT Juja"
}' | tee hustler.json

POSTER_TOKEN=$(jq -r .access_token poster.json)
HUSTLER_TOKEN=$(jq -r .access_token hustler.json)
HUSTLER_ID=$(jq -r .user.id hustler.json)

# 2. Login (sanity check credentials work independently of registration)
curl -s -X POST $BASE/auth/login -H "Content-Type: application/json" -d '{
  "email": "amina@jkuat.ac.ke", "password": "supersecret123"
}'

# 3. Poster creates a gig
curl -s -X POST $BASE/gigs -H "Content-Type: application/json" -H "Authorization: Bearer $POSTER_TOKEN" -d '{
  "title": "Format my essay", "description": "APA formatting, 10 pages, due tomorrow.",
  "budget": "500.00", "gig_type": "TASK_NEEDED", "category": "writing",
  "campus_location": "JKUAT Juja", "is_urgent": true
}' | tee gig.json
GIG_ID=$(jq -r .gig.id gig.json)

# 4. Browse the feed, filtered
curl -s "$BASE/gigs?campus=JKUAT%20Juja&category=writing"

# 5. Hustler applies
curl -s -X POST $BASE/gigs/$GIG_ID/applications -H "Content-Type: application/json" -H "Authorization: Bearer $HUSTLER_TOKEN" -d '{
  "proposal_text": "I can do this in 2 hours."
}' | tee application.json
APPLICATION_ID=$(jq -r .application.id application.json)

# 6. Poster accepts the applicant -> gig moves to IN_PROGRESS
curl -s -X PATCH $BASE/applications/$APPLICATION_ID -H "Content-Type: application/json" -H "Authorization: Bearer $POSTER_TOKEN" -d '{
  "status": "ACCEPTED"
}'

# 7. Either party marks the gig complete
curl -s -X POST $BASE/gigs/$GIG_ID/complete -H "Authorization: Bearer $POSTER_TOKEN"

# 8. Poster reviews the hustler
curl -s -X POST $BASE/reviews -H "Content-Type: application/json" -H "Authorization: Bearer $POSTER_TOKEN" -d "{
  \"gig_id\": $GIG_ID, \"reviewee_id\": $HUSTLER_ID, \"rating\": 5, \"comment\": \"Fast and reliable!\"
}"

# 9. Submit an M-Pesa code for a subscription (manual verification queue)
curl -s -X POST $BASE/payments/verify -H "Content-Type: application/json" -H "Authorization: Bearer $POSTER_TOKEN" -d '{
  "mpesa_code": "QAB1CDE2FG", "purpose": "SUBSCRIPTION"
}' | tee payment.json
PAYMENT_ID=$(jq -r .payment.id payment.json)

# 10. Non-admin is blocked from the admin queue (expect 403)
curl -s -o /dev/null -w "%{http_code}\n" $BASE/admin/payments/pending -H "Authorization: Bearer $POSTER_TOKEN"

# 11. Flag a gig (public reporting endpoint)
curl -s -X POST $BASE/reports -H "Content-Type: application/json" -H "Authorization: Bearer $HUSTLER_TOKEN" -d "{
  \"reason\": \"Suspicious payment request outside the app\", \"reported_gig_id\": $GIG_ID
}"
```

To exercise the admin-only routes (`/admin/payments/pending`,
`/admin/payments/<id>/decision`, `/admin/reports`), flip
`is_admin` to `true` on a user row directly in MySQL first — there's
no self-serve admin signup by design:

```sql
UPDATE users SET is_admin = TRUE WHERE email = 'amina@jkuat.ac.ke';
```