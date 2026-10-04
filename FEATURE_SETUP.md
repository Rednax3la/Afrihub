# Learning, offline, identity, and payment setup

## Combined follow-up deployment (October 2026)

The current frontend host is Vercel (`https://vernaculearn.africa`); backend is Railway (`https://afrihub-production.up.railway.app`). The owner confirmed `main` at `origin` (`Rednax3la/Afrihub`) is the production deployment branch and authorized one combined commit/push. A push is not a health check. The existing MongoDB startup incident is separate; this change does not bypass its startup ping, change database names, or reseed users.

### What appears after deployment

- Mobile and desktop student navigation share Home, Courses, Leaderboard, **Explore**, Profile. Explore contains Games, AI Chat, Videos (all **Coming soon**) and the working Dictionary. Existing `/dictionary` and `/subscription` deep links remain valid.
- Profile uses **Go Premium** or **Manage subscription** based on existing entitlement. Subscription has a normal back link, unchanged monthly/yearly prices, and only the implemented unit-access benefit. Genuine upgrade dialogs keep their close buttons. No new XP spending, tiers, prices, game/video entitlements or production simulation is enabled.
- Checkout first reads `/api/payments/availability`, a no-store configuration-only response with no provider/database call or secret values. Missing providers show a purchase-unavailable message. Google Pay additionally requires matching frontend/backend environments and browser readiness; configuration presence is not proof of merchant approval. Server-side verified-payment and paywall rules remain authoritative.
- Password recovery is present but email delivery requires the configuration and verification below. Foundations appear before the language's numbered units; until reviewed content is imported/published, the destination reports Coming soon. Dictionary keeps current published lesson entries; broader downloaded entries are not auto-published.

### Owner steps, in execution order

1. Check Vercel/Railway deployment logs and independently resolve the MongoDB connectivity incident using the existing database. Do not reseed. Verify normal login and language loading before assessing authenticated performance.
2. Confirm backend `ALLOWED_ORIGINS` contains `https://vernaculearn.africa`, existing `SECRET_KEY` is stable across workers, and frontend `VITE_API_URL=https://afrihub-production.up.railway.app`. Rebuild Vercel when frontend variables change. Use the committed recovery rewrites/CSP in whichever Vercel root directory is configured.
3. Complete SMTP eligibility, regional connection, authentication, verified sender and SPF/DKIM steps in the password section below. These settings are backend Railway variables only. Verify an actual delivery; none has been attempted by this change.
4. Review planned database indexes using `python backend/scripts/ensure_indexes.py` (no connection). In a trusted operator checkout, set the existing backend `MONGODB_URI` and `DB_NAME` privately, then explicitly run `python backend/scripts/ensure_indexes.py --apply`. This adds indexes, not data. No new database name is introduced. Reset-token/rate-limit TTL indexes are also created lazily by reset requests; the DB role needs index permissions. Verify Railway trusted-proxy/client-IP handling for shared rate limits.
5. Review [dictionary sources and real coverage](content/dictionary/SOURCES.md). Collection output lives in ignored `data/dictionary/`; it is not included in deployment. Repeat `python backend/scripts/collect_dictionary.py` from a trusted checkout to obtain the approved sources, retaining hashes and notices. Dry-run `python backend/scripts/import_dictionary.py data/dictionary`, then use `--apply` only after review of the target database. This imports drafts and creates dictionary indexes. To publish a separately curated subset, supply reviewer metadata and use the explicitly documented `--publish-reviewed` dry run before `--publish-reviewed --apply`. Preserve source/history links, CC-BY-SA attribution/share-alike and change notices. Permission-blocked sources must not be scraped. Broader coverage becomes visible only after this publication step.
6. Follow [foundation import/review instructions](content/foundations/README.md) and [tutor recording checklist](content/foundations/TUTOR_RECORDINGS.md). `python backend/scripts/import_foundations.py content/foundations/drafts.json` is a no-connection dry run. `--apply` inserts 56 drafts into a separate collection without touching existing units/progress. Publish only a reviewed subset using `--publish-reviewed --apply`; pronunciation requires consented, reviewed human recordings. If the Railway image only contains `backend/`, run imports from a trusted checkout or explicitly copy the reviewed content artifact to the operator environment. No import or recording has been performed in production.
7. Refresh old PWA tabs when the update notice appears. Verify Explore/deep links, Profile subscription wording, unavailable purchases, legacy login, new-password requirements, recovery privacy, expiry/reuse and session revocation with your own test account. Verify that original unit 3 remains free and unit 4 remains premium, and existing lesson bookmarks/completions still work. Check dictionary direction/marks/attribution and that drafts stay hidden. Offline tests should use previously visited routes under the updated worker; unopened lazy routes need a connection.

### Validation and deferred work

Run mocked backend tests (`tests/test_password_recovery.py`, `tests/test_content_pipeline.py`, `tests/test_learning_features.py`, `tests/test_mpesa_environments.py`), `node --test tests/offline.test.mjs tests/passwords.test.mjs tests/navigation.test.mjs`, and `npm run build`. These tests do not start application servers or verify external services. See [performance evidence](docs/PERFORMANCE.md) for measured public HTTP/build observations versus expected request savings. Live authenticated timing, DB performance, SMTP delivery, merchant readiness, dialect/content approval, recordings, and deployment health remain external verification steps. Durable email delivery, complete games/chat/video infrastructure, broader permitted sources and content-review UI are deferred; consult the current section of `ROADMAP.md`.

## Local setup

- Backend: create a virtual environment, install `backend/requirements.txt`, copy `backend/.env.example` to `backend/.env`, and configure MongoDB and a strong JWT `SECRET_KEY`. Run `uvicorn main:app --reload` from `backend`.
- Frontend: copy `frontend/.env.example` to `frontend/.env`, set `VITE_API_URL` to the backend origin (without `/api`), then run `npm install` and `npm run dev` from `frontend`.
- Verify the PWA using `npm run build` followed by `npm run preview`; automatic service worker registration runs in production builds. Serve all SPA paths as `index.html`. Use HTTPS in deployment; localhost is allowed for development.

## Google sign-in

Create a Google OAuth web client, configure its authorized JavaScript origins for your frontend, and put the same client ID in backend `GOOGLE_CLIENT_ID` and frontend `VITE_GOOGLE_CLIENT_ID`. The backend validates signature, audience, expiry, issuer, and verified email. New Google users are students with no password hash. Google-only accounts cannot use password login. Existing Gmail and verified Workspace accounts can sign in directly; an existing external-email account without a linked Google subject requires password sign-in to avoid unsafe automatic account linking.

The Continue with Google action starts One Tap and renders the standard Google button as a fallback for browsers that suppress One Tap.

## Password recovery and password forms

### Completed code behavior

`POST /api/auth/forgot-password` accepts `{email}` and returns HTTP 202 with the same conditional delivery message for password accounts, Google-only accounts, and unknown addresses. Account lookup, token creation, and SMTP delivery run as an in-process background task **after** that response. A request does not change the account, its password, its sessions, or existing reset links. Missing/invalid email settings return the same HTTP 503 for every address and do not block backend startup or other authentication routes.

`POST /api/auth/reset-password` accepts `{token, password}`. Links contain 32 cryptographically random bytes, expire after 30 minutes, and are stored only as SHA-256 hashes in `password_reset_tokens`. Expiry is enforced in application code, including after bcrypt hashing; MongoDB TTL cleanup is only housekeeping. A single atomic user update compares the token's `session_version`, replaces the password hash, and increments that version. That update consumes the token and invalidates every other outstanding link and JWT from the old version, including concurrent submissions. It needs no MongoDB replica-set transaction. Existing accounts and JWTs without a version default to version zero; they continue working until a successful reset. Google-only accounts cannot acquire a password here. A reset never issues a login token.

New student/tutor registrations and resets require at least 9 characters, ASCII uppercase/lowercase letters, an ASCII digit, and an ASCII punctuation character (for example `!`, `@`, `_`). Spaces are preserved but do not count as punctuation. Bcrypt accepts at most **72 UTF-8 bytes**, not 72 Unicode characters; null characters and longer input are rejected rather than truncated. Login does not impose the new strength policy on existing passwords. A historical password longer than bcrypt's limit must use recovery; its truncated historical representation is not silently accepted. No existing hashes are migrated. There was no existing change-password form or endpoint. Login, both registration forms, and reset/confirmation inputs use accessible show/hide buttons and password-manager autocomplete.

Login distinguishes invalid credentials from a network error or an unavailable backend. Authentication API responses use `Cache-Control: no-store`. Recovery uses a separate first-party HTML entry without Google identity/payment scripts, analytics, or external fonts. Tokens travel in URL fragments, are removed from browser history before the form mounts, and are retained only in page memory. Refreshing the page requires reopening the email link. Recovery pages use `Referrer-Policy: no-referrer` and a restrictive CSP. The service worker never caches or supplies offline fallbacks for recovery pages or auth APIs; the cache version changes to discard old caches.

### Railway backend configuration — owner action required

Set these **only in the backend Railway service**; placeholders in `backend/.env.example` are not production configuration:

| Variable | Required value |
| --- | --- |
| `PASSWORD_RESET_ORIGIN` | `https://vernaculearn.africa` (HTTPS origin only, no path, query, userinfo, or nonstandard port) |
| `SMTP_HOST` | Provider-confirmed outgoing SMTP hostname for your region/account |
| `SMTP_PORT` | Provider-confirmed port (commonly 587 for STARTTLS or 465 for implicit TLS) |
| `SMTP_SECURITY` | Exactly `starttls` or `ssl`; plaintext and TLS fallback are not supported |
| `SMTP_USERNAME` | Provider SMTP login identifier |
| `SMTP_PASSWORD` | Provider-approved SMTP credential or app password, kept secret |
| `SMTP_FROM` | Bare sender email address authorized by the provider |
| `SMTP_TIMEOUT_SECONDS` | Optional socket timeout, default `10`, permitted range 1–30 seconds |

SMTP verifies certificates and hostnames using the system trust store and authenticates only after TLS. The timeout applies to socket operations, not a total delivery deadline. Authentication uses the existing `SECRET_KEY`; keep it strong, stable, and identical across workers. Keep `ALLOWED_ORIGINS` configured to include `https://vernaculearn.africa`. Neither value is changed by this feature.

The backend MongoDB identity needs create-index/read/write access to `password_reset_tokens` and `password_reset_limits` in the **existing database**, plus its existing users access. TTL indexes are created lazily by recovery requests. Limits use atomic MongoDB counters shared across workers: per 15-minute fixed window, requests allow 5 per normalized email and 20 per client IP; confirmations allow 20 per token and 50 per IP. Counter identifiers use keyed hashes. Windows can allow a burst around their boundary; distributed abuse needs additional edge controls. Configure the ASGI server to trust only Railway's verified reverse proxy when deriving the client IP, and verify this in deployment. The app never trusts arbitrary `X-Forwarded-For` itself. Until proxy trust is correct, users may share a proxy IP limit. All processes must share the same database/secret and have synchronized clocks.

### Verify email eligibility before configuring production — owner action required

1. In the actual Zoho Mail account/admin console, check the plan, region/data center, and whether **authenticated outbound SMTP** is enabled for this account. Ask Zoho support if unclear. A Forever Free account and working webmail do **not** establish SMTP eligibility; do not infer it from IMAP availability. No provider connection was attempted during implementation.
2. Obtain the exact outgoing hostname, port/security pair, username, and authentication method shown for your account. Follow [Zoho's SMTP instructions](https://www.zoho.com/mail/help/zoho-smtp.html); do not copy a US-region hostname blindly. If your account requires and permits app-specific passwords (for example with MFA), create a dedicated application password in Zoho Accounts security settings and use it as `SMTP_PASSWORD`. Follow [Zoho's application-password instructions](https://www.zoho.com/mail/help/adminconsole/two-factor-authentication.html). If your plan/policy does not offer this, confirm another supported method with Zoho; this implementation supports SMTP username/password authentication, not OAuth SMTP.
3. Verify the sender/domain in the provider dashboard and authorize the exact `SMTP_FROM` address or alias. Follow the provider's [domain setup](https://www.zoho.com/mail/help/adminconsole/email-hosting-setup.html), [SPF](https://www.zoho.com/mail/help/adminconsole/spf-configuration.html), and [DKIM](https://www.zoho.com/mail/help/adminconsole/dkim-configuration.html) instructions using **your account's generated DNS values**. Merge authorized senders into the domain's existing SPF record; never add a second SPF record. Publish the provider-issued DKIM selector/value and verify it there. Do not alter MX records merely to enable transactional sending.
4. If Zoho Mail SMTP is unavailable, provision an SMTP-capable transactional provider. For example, follow the [Zoho transactional SMTP setup](https://www.zoho.com/zeptomail/help/smtp-home.html), verify your sending domain/sender, obtain that service's regional SMTP credentials, and populate the same variables above. It is a separate service with its own eligibility, quotas, and billing; no provider is automatically enabled by this code. Confirm Railway outbound SMTP availability for your hosting plan before relying on it.

### Vercel build and deep links — owner action required

Set frontend `VITE_API_URL=https://afrihub-production.up.railway.app` and rebuild. There are no new frontend secret variables. Vite now builds both `index.html` and `recovery.html`. Both root and `frontend/` Vercel configurations rewrite `/forgot-password` and `/reset-password` to `recovery.html` **before** the ordinary SPA fallback, with no-store/referrer/CSP headers. The recovery CSP permits the stated Railway API origin; if that origin changes, update both Vercel configs and rebuild. Do not override these routes with a dashboard-level catch-all or inject analytics/scripts into recovery pages. Close old tabs or refresh the service worker before verification; an already installed old worker only updates once clients reload/close. On other hosts, reproduce these exact route/header rules. These pages require a network connection.

### Live verification after the database incident is resolved

- First repair and independently verify the existing Railway MongoDB connectivity/startup incident. This feature does not change database names, bypass the startup ping, reseed accounts, or repair `ServerSelectionTimeoutError`.
- The owner has authorized this combined deployment; resolve the database incident independently before testing data-backed functionality. Confirm both deep links open directly with the recovery HTML and no third-party resources. Check no-store, no-referrer, CSP, CORS, and the active service worker version.
- With an account and inbox you control, request a link, check the generic response and actual email receipt (including spam), the trusted origin, and the 30-minute notice. Confirm unknown/Google-only addresses get the same response. Do not use other people's accounts.
- Reset with a compliant password, verify no automatic login, old-password rejection, new-password success, and revocation of previous JWTs on another online device. Verify reused and expired links fail and every pre-reset outstanding link fails. Confirm old weaker-password accounts can still log in before resetting.
- Check show/hide controls by keyboard, confirmation matching, password-manager suggestions, the rate-limit 429 response, and outage versus wrong-password messages. Confirm the provider accepted the sender and that delivered mail passes the provider-required SPF/DKIM checks.

### Reliability and testing limits

HTTP 202 means a conditional delivery attempt, **not** confirmed delivery. Background tasks are not a durable queue: process restarts/deploys can lose unsent mail, there are no automatic retries or bounce webhooks, and SMTP acceptance does not guarantee inbox placement. Runtime delivery errors are logged as generic warnings without recipient, token, URL, credentials, or message content; failed-delivery token cleanup is attempted. Users may request a new link subject to limits. Missing configuration gets an honest generic 503. Monitor those warnings and provider dashboards; a durable queue is future work. Do not enable request-body logging, SMTP debug logging, or instrumentation that captures credentials/reset bodies.

Session revocation is enforced on subsequent online authenticated requests. Content already downloaded for offline learning cannot be remotely erased by a password reset; the resetting browser clears its local API cache, and other clients clear theirs on logout. Unit tests simulate MongoDB with `mongomock-motor`, force competing reset submissions to overlap, and mock SMTP. They do not prove live SMTP eligibility/delivery, proxy trust, DNS, browser password-manager behavior, or real-cluster performance. Run isolated checks without startup or external services:

```text
cd backend
python -m pytest tests/test_password_recovery.py tests/test_learning_features.py tests/test_mpesa_environments.py -q -p no:cacheprovider
cd ../frontend
node --test tests/offline.test.mjs tests/passwords.test.mjs
npm run build
```

## Subscription and M-Pesa

Units after order 3 require `subscription_status: active`; `expires_at`, when present, is also enforced. Expired accounts lose premium access. The units API returns locked unit metadata and no lesson list. Lesson reads, answer submissions, and completions all enforce the same rule. Legacy `is_premium` alone does not grant access: migrate existing paid users to the new subscription fields after verifying their entitlement.

Configure a Daraja application with consumer key/secret, shortcode, passkey, and a public HTTPS callback URL ending in `/api/payments/mpesa/callback`. Set a long random `MPESA_CALLBACK_SECRET`. The backend appends it to the registered callback URL. Avoid logging callback query strings in your reverse proxy. Use `MPESA_ENVIRONMENT=sandbox` for Daraja testing, and switch to `production` with live credentials for real charges. This implementation uses the PayBill STK transaction type `CustomerPayBillOnline`.

The dashboard modal and subscription page call `POST /api/payments/mpesa/stk-push` with `{phone, tier}`. The server chooses the price (KES 1,299 or 12,999), stores the checkout, and verifies completion using an authenticated Daraja STK query. Callback payloads alone cannot grant access. The frontend polls the authenticated checkout status for up to two minutes and then offers a manual status check; callback processing can complete after the page closes.

M-Pesa sandbox processing requires **both** `APP_ENV=development` and `MPESA_ENVIRONMENT=sandbox`. An unset `APP_ENV` is treated as production; only `sandbox` and `production` are accepted provider environments. Unsafe or incomplete M-Pesa configuration returns HTTP 503 for payment requests without preventing the application from starting. New checkout records store `environment`, which must match the configured provider environment before confirmation. Callbacks and status queries return HTTP 409 with a reconciliation-required message for legacy records without an environment, unsupported recorded environments, or mismatches, including completed records. Do not infer or bulk-fill legacy environments from current deployment settings: reconcile them against verified provider records. This change does not automatically revoke existing subscriptions or migrate old payments.

`PATCH /api/users/me/subscription` accepts the requested status, tier, and ISO expiry, but is restricted to administrators. Allowing students to submit `active` would bypass payment entirely. Both payment handlers call the same internal subscription update function after confirmation instead of making an HTTP request to their own application. Subscription duration is 30/365 days from checkout creation, repeated delivery cannot extend the same payment, and an activation never shortens a later existing expiry. These purchases do not automatically renew or create recurring billing mandates.

## Google Pay

Google Pay returns a payment token; it does not charge a card or offer a standalone payment-verification endpoint. Production uses the supported Stripe gateway and confirms a PaymentIntent before activation. See [Google Pay's payment flow](https://developers.google.com/pay/api/web/overview) and [Stripe PaymentIntents](https://docs.stripe.com/api/payment_intents/create).

For a local simulated checkout, set backend `APP_ENV=development` and `GOOGLE_PAY_ENVIRONMENT=TEST`, and frontend `VITE_GOOGLE_PAY_ENVIRONMENT=TEST`. This deliberately activates without charging; never use those backend settings on a public production service. The backend defaults to production and refuses TEST activation outside development.

For production, set both Google Pay environments to `PRODUCTION`, configure an approved `VITE_GOOGLE_PAY_MERCHANT_ID`, `VITE_STRIPE_PUBLISHABLE_KEY`, and matching backend `STRIPE_SECRET_KEY` from a Stripe merchant account eligible to accept KES payments. Obtain Google Pay production approval for the website. No merchant account or external payment settings were created by this code change. A successful live processor response must confirm the exact amount and currency. Cards requiring additional authentication currently fail without activating access; the UI offers M-Pesa as an alternative. Raw payment tokens are not stored; a digest is used for retry deduplication.

## Web Push

Run `python backend/scripts/generate_vapid_keys.py` from the repository root using the backend virtual environment. It writes private local settings to ignored `backend/.env.push.local` and refuses to replace an existing key pair. Copy its values to backend `.env` or deployment secrets. Set a monitored `VAPID_CLAIM_EMAIL`. Keep the private key stable and secret; browsers subscribe using the public key.

The profile notification switch requests permission only after user interaction, persists the browser subscription, and removes it when disabled. A browser supports one stored endpoint per user in the current schema. Push endpoints are restricted to known browser push services to prevent arbitrary server requests. The scheduler runs daily at 19:00 Africa/Nairobi while the backend process is running; database claims prevent duplicate reminders across processes. Set `ENABLE_STREAK_REMINDERS=false` to disable this job. An always-on backend is needed; missed days are not replayed after an outage. Unreachable/expired push subscriptions are removed on HTTP 404/410.

## Offline and review behavior

The worker caches the app shell and Vite chunks, uses cache-first for local static assets, and network-first for GET API requests. API caches are partitioned by a hash of the login token and cleared on logout. HTTP 401/403 responses never fall back to previously cached access. Pages and data must have been cached before disconnecting; writes, payments, answers, and lesson completion still need a network connection and are not queued. Reconnect to refresh progress and subscription status. Bump cache versions when changing cache formats.

SM-2 stores the next review as an ISO calendar date in Nairobi time and advances from the previous interval/ease factor. Review results are user-scoped, join published lesson/language metadata, and mark premium lessons as locked when access has expired; those review cards open the upgrade modal. Dictionary search escapes regex input and follows the repository's existing convention: `prompt` contains the native phrase, `native_text` contains its English translation. Dictionary results include published vocabulary, including vocabulary in premium units, as requested; full lesson content remains locked.

## Validation

From `backend`, install `requirements-dev.txt` and run `python -m pytest tests/test_learning_features.py -q`. These tests use a mock Motor database and fake external services, never a live account. The existing `tests/test_api.py` is unchanged and remains a separate integration suite; its public-units expectation predates the new authenticated paywall.

From the repository root run `node --test frontend/tests/offline.test.mjs` and `npm --prefix frontend run build`. Before deployment, exercise real Google sign-in, a Daraja sandbox payment, browser notification permissions/delivery, and offline reloads over HTTPS. Those require external credentials or a supported browser/device.

Android packaging instructions are in [bubblewrap/README.md](bubblewrap/README.md). The provided TWA manifest is a starter; a signed Android build and Play upload are separate release steps.
