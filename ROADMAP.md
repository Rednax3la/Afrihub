# Vernaculearn — Product Roadmap
*African Language Learning Platform · Version 1.2 · March 2026 · Confidential*

---

## What is Vernaculearn?
A curriculum-backed, gamified platform for learning African vernacular languages — powered by vetted native-speaking tutors who act as voice characters within the app.

**App Name:** Vernaculearn
**Category:** Ed-Tech / Language Learning
**Initial Languages:** Yoruba, Swahili, Zulu, Amharic (expandable to 50+)
**Target Users:** African diaspora, students, cultural enthusiasts, travellers
**Revenue Model:** Freemium subscription (monthly & yearly)
**Platform:** Web (desktop & mobile) → PWA → Native mobile apps
**Current Stage:** Phase 0–1 complete — stabilised MVP with Admin CMS + Tutor Portal

---

## Architecture: Tutor Model
Instead of partnering with schools, Vernaculearn works with **individual vetted tutors**:
- Tutors apply on the platform and are approved by admins
- Each tutor can be a **voice character** in the app (e.g. "Amara" for Yoruba)
- Tutors upload their own units and lessons via the Tutor Portal
- Content is attributed to their character for a consistent learner experience
- Small, curated tutor roster keeps content quality high and consistent

---

## Tech Stack

### Current
| Layer | Tech |
|---|---|
| Frontend | Vue 3 + Pinia + Tailwind CSS + Vite |
| Backend | FastAPI (Python) — async REST API |
| Database | MongoDB (Motor async driver) |
| Auth | JWT (python-jose) + bcrypt · Roles: student / tutor / admin |

### Planned Additions
| Purpose | Tech |
|---|---|
| Media Storage | Cloudflare R2 (audio & images) |
| Payments | Paystack (Africa) + Stripe (international) |
| AI / LLM | OpenAI GPT-4o (chatbot + content generation) |
| Voice AI | ElevenLabs / Azure TTS (pronunciation, character voices) |
| Automation | n8n (self-hosted) — chatbot workflows, email sequences |
| Mobile | React Native (Expo) |
| Email | Resend or SendGrid |
| Analytics | PostHog |
| Monitoring | Sentry |
| Hosting | Cloudflare Pages (frontend) + Railway/Render (backend) |
| CI/CD | GitHub Actions |

---

## Roles
| Role | Access |
|---|---|
| `student` | Learning dashboard, courses, lessons, profile, subscription |
| `tutor` | Tutor portal — create/edit units & lessons for assigned languages |
| `admin` | Admin portal — full CMS, user management, tutor approvals |

---

## Phase Roadmap

### ✅ Phase 0 — Stabilisation & Fixes *(COMPLETE)*
- Desktop responsive layout across all views
- MongoDB seeded — languages, units, lessons, admin + tutor accounts
- API connections verified (CORS, env variables, proxy)
- End-to-end flow: register → enrol → complete lesson → XP saved in DB

### ✅ Phase 1 — Admin Panel & Tutor Portal *(COMPLETE)*

**Admin Portal** (`/admin/*`, role = `admin`):
- Dashboard with platform stats (students, tutors, languages, lessons)
- User management — view, toggle premium, delete users
- Tutor management — approve / suspend tutor applications with status badges
- Content CMS — full CRUD for languages, units, lessons & questions (inline editor)

**Tutor Portal** (`/tutor/*`, role = `tutor`):
- Dashboard — content stats, voice character card, languages taught
- Content manager — create/edit/delete units and lessons with question editor
- Profile editor — name, bio, avatar URL, voice character name
- Pending approval banner for newly registered tutors

**Auth updates:**
- Tutor registration at `/register/tutor` — bio, language selection, voice character
- Login redirects by role: admin → `/admin/dashboard`, tutor → `/tutor/dashboard`
- Role-based route guards throughout Vue Router
- `isAdmin`, `isTutor`, `isStudent` computed properties in auth store

**Seed accounts:**
- Admin: `admin@vernaculearn.com` / `Admin1234!`
- Tutors: `amara@vernaculearn.com` / `juma@vernaculearn.com` — password `Tutor1234!`

### 🔵 Phase 2 — Rich Content & Audio *(PLANNED · Month 2–3)*
- Audio upload & playback — native speaker recordings on phrases/questions
- Text-to-Speech fallback — AI-generated audio (ElevenLabs / Azure TTS)
- Image-based questions — "What does this image show?"
- Listening comprehension — play audio clip, choose correct translation
- Cultural notes — proverbs, traditions, history tied to lesson content
- Cloudflare R2 for media storage

### 🔵 Phase 3 — Gamification & Retention *(PLANNED · Month 3–5)*
- Spaced repetition system (SRS)
- Dynamic streak system — shields, comeback bonuses
- Weekly leaderboard per language
- 50+ badges & achievement system
- Downloadable PDF certificates
- Level system: Bronze → Silver → Gold → Platinum
- Hearts/lives system
- Push notifications (PWA + email)
- An online sourced Translator/Dictionary between English and Kenyan vernacular languages

### 🔵 Phase 4 — Mobile App & Offline Mode *(PLANNED · Month 5–7)*
- Progressive Web App (PWA) — installable, works offline
- Service worker caching
- React Native mobile app (iOS + Android)
- Download packs for offline study
- App Store & Google Play launch
- Low-data mode for 2G networks

### 🔵 Phase 5 — Payments *(PLANNED · Month 6–8)*
- Paystack — cards, mobile money, bank transfer
- Stripe — USD/GBP/EUR for diaspora users
- Monthly ($5.99) & yearly ($49.99) with 7-day free trial
- Corporate accounts
- Gift subscriptions

### 🔵 Phase 6 — AI Features & Chatbot *(PLANNED · Month 8–11)*
- n8n-powered AI language tutor chatbot
- Adaptive learning path
- AI pronunciation scorer
- AI lesson generator (tutors describe topic → AI drafts questions)
- Conversational practice mode
- Smart error analysis post-lesson

### ⚫ Phase 7 — Community & Scale *(FUTURE · Month 11–18)*
- Live 1-on-1 tutoring marketplace (20% commission)
- Group live classes streamed in-app
- Community forums per language
- Language exchange matching
- Analytics platform for tutors
- API & white-label licensing

---

## Immediate Next Steps
1. `cd backend && python seed.py` — populates DB with seed data + accounts
2. Test admin login and CMS flows
3. Test tutor registration → admin approval → tutor content creation
4. Deploy backend to Railway/Render, frontend to Cloudflare Pages
5. Begin Phase 2: audio upload + Cloudflare R2 integration

---

*Vernaculearn · Preserving Africa's languages, one lesson at a time.*
