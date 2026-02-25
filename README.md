# 🌍 Afrihub — African Language Learning App

> Duolingo, but for African vernacular languages. Built with Vue 3, FastAPI, and MongoDB.

---

## Project Structure

```
afrihub/
├── .gitignore
├── docker-compose.yml
├── backend/          ← FastAPI + MongoDB
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── main.py       ← App entry point
│   ├── database.py   ← MongoDB connection
│   ├── auth.py       ← JWT + password hashing
│   ├── seed.py       ← Populate DB with sample data
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lesson.py
│   │   └── progress.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py       ← /api/auth/register, /api/auth/login
│   │   ├── users.py      ← /api/users/me
│   │   ├── lessons.py    ← /api/languages, /api/lessons, /api/lessons/answer
│   │   └── progress.py   ← /api/progress/me
│   └── tests/
│       ├── __init__.py
│       └── test_api.py
│
└── frontend/         ← Vue 3 + Pinia + Tailwind CSS
    ├── .env.example
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── jsconfig.json
    ├── eslint.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── style.css
        ├── views/
        │   ├── SplashView.vue       ← Landing page
        │   ├── LoginView.vue
        │   ├── RegisterView.vue
        │   ├── DashboardView.vue    ← Learning path
        │   ├── CoursesView.vue      ← Browse all languages
        │   ├── LessonView.vue       ← Interactive quiz
        │   ├── SubscriptionView.vue
        │   ├── ProfileView.vue
        │   └── NotFoundView.vue     ← 404 page
        ├── stores/
        │   ├── auth.js              ← Login, register, logout
        │   ├── content.js           ← Languages, units, lessons
        │   └── progress.js          ← User progress
        ├── composables/
        │   └── useLesson.js         ← Quiz state logic
        ├── api/
        │   └── index.js             ← Axios API client
        ├── router/
        │   └── index.js             ← Vue Router
        └── components/
            ├── BottomNav.vue
            ├── LanguageCard.vue
            ├── LoadingSpinner.vue
            └── StatBadge.vue
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB running locally on port 27017

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy env file and configure
cp .env.example .env
# Edit .env — at minimum set a strong SECRET_KEY

# Seed the database with languages, units, and lessons
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

App available at: http://localhost:5173

---

## Key Features Connected (Frontend ↔ Backend)

| Feature | Endpoint |
|---|---|
| Register | `POST /api/auth/register` |
| Login | `POST /api/auth/login` |
| Get profile | `GET /api/users/me` |
| Browse languages | `GET /api/languages` |
| Enroll in language | `POST /api/users/me/languages/{id}` |
| Load units | `GET /api/languages/{id}/units` |
| Load lesson | `GET /api/lessons/{id}` |
| Submit answer | `POST /api/lessons/answer` |
| Complete lesson | `POST /api/lessons/{id}/complete` |

---

## What Was Added (The Missing Page)

The **Courses** page (`/courses`) was missing from the original design. It now includes:
- Full language browser with search
- Region filter tabs
- Enrolled / not enrolled states
- Premium language locking
- Partner school cards
- One-tap enroll into any language

---

## Next Steps

- [ ] Add audio playback for lesson phrases
- [ ] Streak tracking cron job
- [ ] Leaderboard endpoint
- [ ] Payment integration (Stripe / Paystack for African markets)
- [ ] Offline lesson caching (PWA)
- [ ] Admin panel for adding new content
