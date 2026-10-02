# Learning, offline, identity, and payment setup

## Local setup

- Backend: create a virtual environment, install `backend/requirements.txt`, copy `backend/.env.example` to `backend/.env`, and configure MongoDB and a strong JWT `SECRET_KEY`. Run `uvicorn main:app --reload` from `backend`.
- Frontend: copy `frontend/.env.example` to `frontend/.env`, set `VITE_API_URL` to the backend origin (without `/api`), then run `npm install` and `npm run dev` from `frontend`.
- Verify the PWA using `npm run build` followed by `npm run preview`; automatic service worker registration runs in production builds. Serve all SPA paths as `index.html`. Use HTTPS in deployment; localhost is allowed for development.

## Google sign-in

Create a Google OAuth web client, configure its authorized JavaScript origins for your frontend, and put the same client ID in backend `GOOGLE_CLIENT_ID` and frontend `VITE_GOOGLE_CLIENT_ID`. The backend validates signature, audience, expiry, issuer, and verified email. New Google users are students with no password hash. Google-only accounts cannot use password login. Existing Gmail and verified Workspace accounts can sign in directly; an existing external-email account without a linked Google subject requires password sign-in to avoid unsafe automatic account linking.

The Continue with Google action starts One Tap and renders the standard Google button as a fallback for browsers that suppress One Tap.

## Subscription and M-Pesa

Units after order 3 require `subscription_status: active`; `expires_at`, when present, is also enforced. Expired accounts lose premium access. The units API returns locked unit metadata and no lesson list. Lesson reads, answer submissions, and completions all enforce the same rule. Legacy `is_premium` alone does not grant access: migrate existing paid users to the new subscription fields after verifying their entitlement.

Configure a Daraja application with consumer key/secret, shortcode, passkey, and a public HTTPS callback URL ending in `/api/payments/mpesa/callback`. Set a long random `MPESA_CALLBACK_SECRET`. The backend appends it to the registered callback URL. Avoid logging callback query strings in your reverse proxy. Use `MPESA_ENVIRONMENT=sandbox` for Daraja testing, and switch to `production` with live credentials for real charges. This implementation uses the PayBill STK transaction type `CustomerPayBillOnline`.

The dashboard modal and subscription page call `POST /api/payments/mpesa/stk-push` with `{phone, tier}`. The server chooses the price (KES 1,299 or 12,999), stores the checkout, and verifies completion using an authenticated Daraja STK query. Callback payloads alone cannot grant access. The frontend polls the authenticated checkout status for up to two minutes and then offers a manual status check; callback processing can complete after the page closes.

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
