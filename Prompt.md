# CLAUDE CODE PROMPT — Vernaculearn Phase 2+ Completion

Copy everything below this line into Claude Code in VS Code. Open the project folder (`Afrihub/`) first so Claude Code has the full repo context.

---

## CONTEXT

You are working on **Vernaculearn** (repo: `Afrihub/`), an African language learning platform — think Duolingo for African vernacular languages. The tech stack is **Vue 3 + Pinia + Tailwind CSS** (frontend) and **FastAPI + MongoDB (Motor)** (backend).

**Phases 0 and 1 are complete**: basic auth, lesson flow, admin CMS, tutor portal with content CRUD. The app has 59 commits and is deployed at vernaculearn.vercel.app.

I need you to complete **Phase 2 (Rich Content & Audio)** and fix all frontend-backend integration gaps. I'll describe exactly what exists and what's missing. Do NOT rewrite working code — only add what's missing and fix what's broken.

---

## CURRENT FILE STRUCTURE (key files only)

```
backend/
  main.py                    ← FastAPI app, CORS, route registration, serves /uploads static
  auth.py                    ← JWT auth, get_current_user, require_active_tutor
  database.py                ← Motor async MongoDB connection
  seed.py                    ← Seeds languages, units, lessons, users (admin + 2 tutors)
  requirements.txt           ← fastapi, motor, python-jose, passlib, aiofiles, python-multipart
  models/
    user.py                  ← UserRegister, TutorRegister, UserLogin, UserPublic, etc.
    lesson.py                ← Question (with audio_url, image_url), Lesson (with cultural_note, audio_intro_url), Unit, Language
    progress.py              ← LessonProgress, UnitProgress, LanguageProgress, UserProgress
  routes/
    auth.py                  ← POST /api/auth/register, /api/auth/login, /api/auth/register/tutor
    users.py                 ← GET/PATCH /api/users/me, POST /api/users/me/languages/{id}
    lessons.py               ← GET /api/languages, /api/lessons/{id}, POST /api/lessons/answer, /api/lessons/{id}/complete
    progress.py              ← GET /api/progress/me
    admin.py                 ← Full CRUD for languages/units/lessons/users/tutors
    tutors.py                ← Tutor profile, content CRUD (GET/POST/PATCH/DELETE own units + lessons)
    upload.py                ← POST /api/upload/audio, /api/upload/image (saves to local filesystem)
  uploads/                   ← Local upload directory (served as static via FastAPI)

frontend/src/
  api/index.js               ← Axios client with all API endpoints (auth, content, admin, tutor, upload)
  stores/
    auth.js                  ← Login, register, logout, user state
    content.js               ← Languages, units, lessons fetching
    progress.js              ← User progress
    admin.js                 ← Admin store
    tutor.js                 ← Tutor content CRUD (units + lessons)
    toast.js                 ← Toast notifications
  composables/
    useLesson.js             ← Quiz state machine (loads lesson, handles answers, cultural notes, audio intro)
  components/
    AudioPlayer.vue          ← Simple audio playback component (EXISTS but basic)
    FileUpload.vue           ← Drag-drop + URL paste for audio/image uploads (EXISTS and works)
    BottomNav.vue, SideNav.vue, LanguageCard.vue, Modal.vue, Toast.vue, etc.
  views/
    LessonView.vue           ← Quiz screen — handles translate, multiple_choice, listen, image question types
    DashboardView.vue        ← Learning path
    CoursesView.vue          ← Language browser with search + region filter
    ProfileView.vue, LoginView.vue, RegisterView.vue, etc.
    admin/                   ← AdminDashboardView, AdminContentView, AdminTutorsView, AdminUsersView, AdminLayout
    tutor/                   ← TutorDashboardView, TutorContentView (lesson/unit CRUD with question editor), TutorProfileView, TutorLayout
```

---

## WHAT ALREADY EXISTS (DO NOT REBUILD)

These features are already scaffolded and working. Do not rewrite them:

1. **Lesson model** already has `audio_url`, `image_url`, `audio_intro_url`, `cultural_note`, `cultural_note_title` fields
2. **Question model** already has `type` field supporting "translate", "multiple_choice", "listen", "image"
3. **LessonView.vue** already renders all 4 question types with AudioPlayer and image display
4. **useLesson.js** composable already handles audioIntroUrl, culturalNote loading and display
5. **FileUpload.vue** already handles drag-drop upload + URL paste for both audio and images
6. **TutorContentView.vue** already has the FileUpload wired into the question editor for listen/image types
7. **Upload routes** (`/api/upload/audio`, `/api/upload/image`) work with local filesystem
8. **Admin CMS** has full CRUD for languages, units, lessons
9. **Tutor portal** has content CRUD (create/edit/delete own units + lessons)
10. **Auth** works with JWT + role-based guards (student/tutor/admin)

---

## PHASE 2 GAPS — WHAT'S MISSING (BUILD THESE)

### 2A. Cloudflare R2 Media Storage (replace local uploads)

**Current state**: `routes/upload.py` saves files to `backend/uploads/` on the local filesystem. This won't work in production (Vercel/Railway ephemeral filesystems).

**What to build**:
- Replace the upload route to use **Cloudflare R2** (S3-compatible API)
- Add `boto3` to `requirements.txt`
- Add env vars: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`
- Upload to R2, return the public URL
- Keep the same API contract (`POST /api/upload/audio` → `{ url, filename }`) so the frontend FileUpload.vue doesn't need changes
- Add a `R2_ENABLED` env var — if false, fall back to local storage (for local dev)
- Update `.env.example` with the new vars

### 2B. Text-to-Speech Fallback

**Current state**: Audio only plays if a pre-uploaded file URL exists. No TTS fallback.

**What to build**:
- New backend endpoint: `POST /api/tts/generate` — accepts `{ text, language_code }`, returns `{ audio_url }`
- Use **ElevenLabs API** as primary (env var `ELEVENLABS_API_KEY`), with a fallback to **Google Cloud TTS** or **gTTS** (free, offline)
- The endpoint should:
  1. Check if a cached TTS file already exists for this text+language combo (hash-based filename)
  2. If cached, return existing URL
  3. If not, generate via ElevenLabs (or fallback), upload to R2 (or local), return URL
- Add `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_IDS` (JSON mapping language_code → voice_id) to `.env.example`
- Add `gtts` and `requests` to `requirements.txt` as fallback
- Frontend integration: in `LessonView.vue`, if a question has `type: "translate"` and no `audio_url`, show a "🔊 Hear pronunciation" button that calls the TTS endpoint on click and plays the result
- Also add TTS button to the lesson prompt area for all question types that have a `prompt` in a non-English language

### 2C. Cultural Notes System (enrich existing scaffold)

**Current state**: `cultural_note` and `cultural_note_title` fields exist on the Lesson model, the composable reads them, and LessonView.vue displays them. But there's no way for tutors to add them through the UI, and the seed data doesn't include any.

**What to build**:
- In `TutorContentView.vue` lesson modal: add "Cultural Note" section with:
  - Title input (`cultural_note_title`)
  - Textarea for the note body (`cultural_note`)
  - These fields should be passed through when saving the lesson (they already exist in the model)
- In `AdminContentView.vue` lesson editor: same cultural note fields
- In `seed.py`: add cultural notes to at least 2 of the existing seed lessons, for example:
  - Yoruba Unit 1 Lesson 1: cultural note about Yoruba greeting customs (time-of-day greetings, prostrating for elders)
  - Swahili Unit 1 Lesson 1: cultural note about "Mambo/Poa" call-and-response culture
- Add a new `cultural_notes` MongoDB collection for standalone cultural content (proverbs, traditions, history) that can be linked to lessons:
  ```
  { id, language_id, title, body, category: "proverb"|"tradition"|"history"|"etymology", related_unit_ids: [], source: "tutor"|"scraped" }
  ```
- New API endpoints:
  - `GET /api/languages/{id}/cultural-notes` — list cultural notes for a language
  - `POST /api/tutors/me/cultural-notes` — tutor creates a cultural note
  - `PATCH /api/tutors/me/cultural-notes/{id}` — tutor edits own note

### 2D. Listening Comprehension Enhancement

**Current state**: "listen" question type exists — it plays audio and shows text options. But it's just "hear word, pick translation." There's no deeper comprehension.

**What to build**:
- Add new question type: `"listen_comprehension"` — plays a longer audio clip (a sentence or short dialogue), then asks a comprehension question about it (not just translation)
- In `LessonView.vue`: add handling for this type — show audio player prominently, then show the comprehension question and options below
- In the tutor lesson editor (`TutorContentView.vue`): add "Listen Comprehension" to the question type dropdown
- In `useLesson.js`: add label mapping for the new type
- Question schema for this type:
  ```json
  {
    "type": "listen_comprehension",
    "prompt": "What is the speaker asking about?",
    "audio_url": "https://...",
    "options": [...],
    "correct_answer_id": "b"
  }
  ```

### 2E. Scraped Content Review System

**Current state**: No mechanism for reviewing externally sourced content. The scraping pipeline (being built separately via OpenClaw) will insert lessons with `status: "pending_review"` and `source: "scraped"`.

**What to build**:
- Backend: In `routes/admin.py`, add:
  - `GET /api/admin/review-queue` — returns all lessons where `status == "pending_review"`, grouped by language
  - `PATCH /api/admin/lessons/{id}/approve` — sets `status: "published"`
  - `PATCH /api/admin/lessons/{id}/reject` — sets `status: "rejected"`
  - `GET /api/admin/review-queue/stats` — count of pending items per language
- Backend: In `routes/tutors.py`, add:
  - `GET /api/tutors/me/review-queue` — returns pending_review lessons for the tutor's assigned languages
  - `PATCH /api/tutors/me/review/{lesson_id}/approve` — tutor approves (sets status: "published")
  - `PATCH /api/tutors/me/review/{lesson_id}/reject` — tutor rejects
- Frontend: New view `AdminReviewView.vue` in `views/admin/`:
  - Shows pending content grouped by language
  - For each lesson: show questions in a preview, approve/reject buttons
  - Ability to edit questions before approving
- Frontend: In `TutorDashboardView.vue`: add a "Review Queue" card showing count of pending items for their languages
- Frontend: New view `TutorReviewView.vue` in `views/tutor/`:
  - Similar to admin review but filtered to tutor's languages
- Update `routes/lessons.py`: the `GET /api/lessons/{id}` endpoint should only return lessons where `status == "published"` (or status field is absent for backward compatibility with existing data)
- Update `routes/lessons.py`: the `GET /api/languages/{id}/units` endpoint should only return units that have at least one published lesson
- Add routes to `router/index.js` for the new review views

### 2F. Image-Based Questions Enhancement

**Current state**: Image questions show an image and ask "What does this show?" with text answer options. Basic but functional.

**What to build**:
- Add question type `"image_translate"` — shows an image of an object and asks the learner to select the correct word in the target language (reverse of current: current shows foreign word, this shows image)
- Add question type `"image_match"` — shows 4 small images and asks which one matches a given word/phrase
- Handle both in LessonView.vue with appropriate layouts
- Add to the question type dropdown in tutor and admin lesson editors

---

## FRONTEND-BACKEND INTEGRATION GAPS (FIX THESE)

### Gap 1: Lesson Modal Missing Fields

In `TutorContentView.vue`, the lesson create/edit modal is missing:
- `cultural_note` textarea
- `cultural_note_title` input
- `audio_intro_url` upload (FileUpload component for lesson intro audio)
- `status` selector (draft / published)

The same fields should also be added to the admin lesson editor in `AdminContentView.vue`.

### Gap 2: Seed Data Has No Audio/Image Content

`seed.py` only creates text-based translate/multiple_choice questions. Add:
- At least 2 "listen" type questions with placeholder `audio_url` values (can be null or a placeholder URL)
- At least 1 "image" type question with a placeholder `image_url`
- Cultural notes on at least 2 lessons
- This makes the UI actually testable for all question types

### Gap 3: Progress Route Doesn't Track Per-Question Accuracy

`routes/progress.py` tracks lesson completion but not which specific questions the user got wrong. This matters for the spaced repetition system (Phase 3).

**Add to the progress collection**:
```python
# When a lesson is completed, store per-question results
{
    "user_id": "...",
    "lesson_id": "...",
    "questions_attempted": [
        { "question_id": "q1", "correct": True, "answer_given": "a" },
        { "question_id": "q2", "correct": False, "answer_given": "c", "correct_answer": "b" },
    ],
    "score": 75,
    "completed_at": "...",
    "attempt_number": 1
}
```

Update `POST /api/lessons/{id}/complete` to accept this data. Update `useLesson.js` to collect and send per-question results when finishing.

### Gap 4: Dashboard Shows No Lesson-Level Progress

`DashboardView.vue` shows enrolled languages but doesn't show which lessons within a unit are completed vs. locked vs. available. The Duolingo-style learning path needs:
- Fetch user progress and mark completed lessons with a checkmark
- Show the "current" lesson (next uncompleted) highlighted
- Grey out/lock lessons that come after uncompleted ones (linear progression)
- Show unit-level progress bars

### Gap 5: No Streak Tracking

The user model has a `streak` field but nothing updates it. Add:
- Backend: On lesson completion, check if user completed a lesson yesterday → increment streak. If gap > 1 day → reset to 1. If same day → no change.
- Frontend: Show streak on Dashboard and Profile with a fire icon
- Store `last_activity_date` on the user document

### Gap 6: No Language-Specific Keyboard Support

For languages with special characters (Yoruba: ẹ, ọ, ṣ, tonal marks; Amharic: Ge'ez script), there needs to be a way to input these characters.

**What to build**:
- New component: `SpecialCharKeyboard.vue`
  - Props: `language_code` — determines which special characters to show
  - Shows a row of special character buttons above the text input
  - Clicking a button inserts the character at cursor position
  - Character maps:
    - `yo` (Yoruba): ẹ, Ẹ, ọ, Ọ, ṣ, Ṣ, à, á, è, é, ì, í, ò, ó, ù, ú, ǹ, ń
    - `am` (Amharic): needs full Ge'ez script keyboard — defer to system keyboard recommendation for now, but add a toggle that says "Switch to Amharic keyboard" with instructions
    - `zu` (Zulu): standard Latin + click consonants display guide
    - `sw` (Swahili): standard Latin (no special chars needed)
- Add this component to LessonView.vue for question types where the user might need to type (future free-response questions)
- Also add to TutorContentView.vue so tutors can input special characters when creating questions
- Store character maps in a new file: `frontend/src/data/keyboards.js`

### Gap 7: Mobile Responsiveness Gaps

The app claims mobile support but several views have issues on small screens:
- `TutorContentView.vue`: modal overflows on mobile, question editor is cramped
- `AdminContentView.vue`: same modal issues
- `CoursesView.vue`: region filter tabs don't scroll horizontally on narrow screens
- `DashboardView.vue`: unit cards need mobile optimization

Add `overflow-x-auto` to horizontal scrollable areas, ensure modals use `max-h-[80vh] overflow-y-auto`, and test all interactive elements at 375px width.

---

## PHASE 3 PREP (SCAFFOLD ONLY, don't fully implement)

While building Phase 2, add these scaffolds so Phase 3 is easier:

1. **Spaced Repetition**: Add a `review_schedule` field to the progress documents: `{ next_review_date, interval_days, ease_factor }`. Don't build the algorithm yet, just the data structure.

2. **Leaderboard**: Add a `GET /api/leaderboard/{language_id}` endpoint that returns top 20 users by XP for that language. Simple query, no complex ranking.

3. **Badges**: Add a `badges` collection scaffold: `{ id, name, description, icon, criteria_type, criteria_value }`. Add 5 seed badges (First Lesson, 7-Day Streak, 100 XP, 10 Lessons, Perfect Score).

---

## IMPLEMENTATION ORDER

Do these in order to avoid breaking dependencies:

1. **Gap 2** (seed data) — so you can test everything as you build
2. **2A** (R2 storage) — infrastructure needed by everything else
3. **Gap 1** (lesson modal fields) — quick fix, unblocks tutor testing
4. **2B** (TTS) — depends on R2 for storage
5. **2C** (cultural notes system) — depends on tutor modal fix
6. **2D** (listening comprehension) — depends on TTS + audio infrastructure
7. **2F** (image question types) — independent, can be done anytime
8. **2E** (review system) — depends on admin/tutor portals being complete
9. **Gap 3** (progress tracking) — can be done anytime
10. **Gap 4** (dashboard progress) — depends on Gap 3
11. **Gap 5** (streaks) — depends on progress
12. **Gap 6** (keyboards) — independent, can be done anytime
13. **Gap 7** (mobile) — do last as a polish pass
14. **Phase 3 scaffolds** — do alongside as you touch related files

---

## CODING STANDARDS

- **Backend**: Use async/await everywhere (Motor is async). Type hints on all function signatures. Error responses as `HTTPException` with specific status codes and messages.
- **Frontend**: Composition API with `<script setup>`. Tailwind for all styling — no scoped CSS unless absolutely necessary. Use the existing component patterns (Modal, Toast, FileUpload).
- **IDs**: Use the existing pattern — hyphenated slugs like `yoruba-unit-1`, `swahili-u1-l1`.
- **API client**: Add new endpoints to the existing `frontend/src/api/index.js` following the existing pattern.
- **Stores**: Add new Pinia stores only if needed. Extend existing stores where possible.
- **Routes**: Register new Vue Router routes in `frontend/src/router/index.js` following the existing guard pattern.
- **Git**: Make atomic commits. One feature per commit. Commit messages like `feat: add R2 storage integration` or `fix: add cultural note fields to tutor lesson modal`.

---

## ENV VARS TO ADD

Add these to `backend/.env.example`:

```bash
# Cloudflare R2 (media storage)
R2_ENABLED=false
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=vernaculearn-media
R2_PUBLIC_URL=https://media.vernaculearn.com

# Text-to-Speech
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_IDS={"yo": "voice_id_here", "sw": "voice_id_here", "zu": "voice_id_here", "am": "voice_id_here"}
TTS_FALLBACK=gtts

# Existing (unchanged)
MONGODB_URI=mongodb://localhost:27017
DB_NAME=vernaculearn
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://vernaculearn.vercel.app
```

Add to `requirements.txt`:

```
boto3==1.35.0
gtts==2.5.3
```

---

## IMPORTANT NOTES

- The scraping pipeline (OpenClaw) is being built separately. It will insert documents with `source: "scraped"` and `status: "pending_review"` into the units and lessons collections. Your job is to make sure the app can handle these fields gracefully — filter them from student-facing queries and provide review UIs.
- The existing `upload.py` route works fine for local dev. The R2 integration should be a _replacement_ that falls back to local when `R2_ENABLED=false`.
- The `FileUpload.vue` component already works correctly — it posts to `/api/upload/audio` or `/api/upload/image` and gets back `{ url }`. Don't change this component; only change the backend route it hits.
- When adding new question types, always add them to BOTH the tutor editor dropdown AND the admin editor dropdown AND the LessonView.vue rendering AND the useLesson.js type label mapping.
- Test every new endpoint with the existing seed data. Run `python seed.py` before testing.