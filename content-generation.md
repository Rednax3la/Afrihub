# CONTENT GENERATION + READING LESSONS — Claude Code Prompt

You have one week to a pitch. This prompt does three things: generates real lesson content for all 14 languages using the Anthropic API, implements a "reading card" lesson type for text-based learning, and seeds everything into MongoDB following the universal 12-unit curriculum sequence.

## PART 1: IMPLEMENT THE READING CARD LESSON TYPE

Before generating content, add the infrastructure for text-based learning.

### Backend — add `lesson_type` field to Lesson model

In `backend/models/lesson.py`, add to the Lesson class:
```python
lesson_type: str = "quiz"  # "quiz" | "reading" | "flashcard"
reading_content: Optional[str] = None  # For reading lessons — the text to display
```

### Frontend — LessonView reading card

In `frontend/src/views/LessonView.vue`, add a new top-level template block (before the quiz screen) that handles `lesson_type === "reading"`:

```html
<!-- ── READING CARD SCREEN ──────────────────────────────────────── -->
<div v-else-if="lesson.lessonType === 'reading'" class="flex-1 flex flex-col">
  <!-- Header with close + progress -->
  <header class="px-6 pt-6 pb-4 flex items-center gap-4">
    <RouterLink to="/dashboard" class="w-10 h-10 flex items-center justify-center text-slate-400 shrink-0">
      <span class="material-icons-outlined">close</span>
    </RouterLink>
    <div class="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
      <div class="h-full bg-[#00A3C1] rounded-full w-full transition-all duration-500"></div>
    </div>
    <div class="flex items-center gap-1 shrink-0 bg-amber-50 px-3 py-1.5 rounded-full">
      <span class="material-icons-outlined text-amber-500 text-sm">bolt</span>
      <span class="font-bold text-amber-700 text-sm">+{{ lesson.xpEarned }}</span>
    </div>
  </header>

  <main class="flex-1 px-6 py-4 overflow-y-auto">
    <p class="text-xs font-bold tracking-widest text-[#0D9488] uppercase mb-4">Read & Learn</p>

    <!-- Reading card -->
    <div class="bg-white border border-slate-100 rounded-[2rem] shadow-sm p-6 mb-6">
      <h2 class="text-2xl font-bold text-[#003B5C] mb-4">{{ lesson.lessonTitle }}</h2>
      <div class="prose prose-slate max-w-none">
        <p class="text-slate-700 leading-relaxed text-base whitespace-pre-line">{{ lesson.readingContent }}</p>
      </div>
    </div>

    <!-- Vocabulary highlights (if questions exist, treat them as vocab cards) -->
    <div v-if="lesson.questions.length" class="space-y-3">
      <p class="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3">Key Vocabulary</p>
      <div v-for="q in lesson.questions" :key="q.id"
        class="bg-[#A7FFEB]/20 border border-[#00A3C1]/20 rounded-2xl p-4 flex items-center gap-4">
        <div class="flex-1">
          <p class="font-bold text-[#003B5C] text-lg">{{ q.prompt }}</p>
          <p class="text-slate-500 text-sm mt-0.5">{{ q.native_text }}</p>
        </div>
        <button v-if="q.audio_url || lesson.languageCode"
          @click="fetchTTSForWord(q.prompt, q.id)"
          class="w-10 h-10 bg-white border border-[#00A3C1]/30 rounded-xl flex items-center justify-center text-[#00A3C1]">
          <span class="material-icons-outlined text-xl">volume_up</span>
        </button>
      </div>
    </div>
  </main>

  <footer class="px-6 pb-8 pt-2">
    <button
      @click="lesson.completeReading()"
      class="w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform">
      Got it — Continue
    </button>
  </footer>
</div>
```

### useLesson.js updates

Add these refs and the `completeReading` function:
```js
const lessonType   = ref('quiz')
const lessonTitle  = ref('')
const readingContent = ref(null)

// In load():
lessonType.value     = data?.lesson_type ?? 'quiz'
lessonTitle.value    = data?.title ?? ''
readingContent.value = data?.reading_content ?? null

// New function:
async function completeReading() {
  try {
    await contentApi.completeLesson(lessonId, 100, [])
    const authStore = (await import('@/stores/auth')).useAuthStore()
    await authStore.fetchMe()
  } catch { /* non-blocking */ }
  if (culturalNote.value) {
    pendingCulturalNote.value = true
  } else {
    finished.value = true
  }
}

// In return statement, add: lessonType, lessonTitle, readingContent, completeReading
```

## PART 2: CREATE THE CONTENT GENERATION SCRIPT

Create `backend/generate_content.py`. This script calls the Anthropic API to generate structured lesson content for all 14 languages following the 12-unit curriculum, then upserts everything into MongoDB.

```python
"""
Vernaculearn Content Generator
Generates structured lesson content for all 14 languages using Claude API.
Run: python generate_content.py --language kikuyu
     python generate_content.py --all
     python generate_content.py --priority  (Kikuyu + Swahili only)
"""

import anthropic
import asyncio
import json
import hashlib
import os
import time
import argparse
import random
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Universal 12-unit curriculum sequence ────────────────────────────────────
UNITS = [
    {
        "order": 1,
        "title": "Greetings & Farewells",
        "subtitle": "Open every door with the right words",
        "icon": "waving_hand",
        "description": "Time-of-day greetings, hello/goodbye, how are you, thank you, please, sorry, responding to elders",
        "vocab_count": 20,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 2,
        "title": "Introducing Yourself",
        "subtitle": "Tell your story in your language",
        "icon": "person",
        "description": "My name is, I am from, I live in, I am X years old, I am a student/teacher, nice to meet you, asking someone's name, introducing a third person",
        "vocab_count": 18,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 3,
        "title": "Family & Relationships",
        "subtitle": "The people who matter most",
        "icon": "family_restroom",
        "description": "Mother, father, siblings, grandparents, children, husband, wife, friend, neighbour, clan/community words, terms of endearment for elders",
        "vocab_count": 22,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 4,
        "title": "Numbers & Time",
        "subtitle": "Count, plan, and stay on time",
        "icon": "schedule",
        "description": "Numbers 1–20, tens to 100, today/tomorrow/yesterday, morning/afternoon/evening/night, days of the week, months, what time is it, how long",
        "vocab_count": 30,
        "lesson_type_mix": ["reading", "quiz", "quiz", "quiz"],
    },
    {
        "order": 5,
        "title": "The Body & Health",
        "subtitle": "Know yourself, express yourself",
        "icon": "health_and_safety",
        "description": "Body parts (head, hand, eye, mouth, ear, nose, foot, stomach, heart), I am sick, I have pain, I am hungry/thirsty/tired/well, visiting the sick",
        "vocab_count": 20,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 6,
        "title": "Food & Drink",
        "subtitle": "Traditional tastes and everyday meals",
        "icon": "restaurant",
        "description": "Common foods (especially traditional dishes), water, tea, milk, I want to eat, I am full, it is delicious, cooking verbs, traditional meal names, food-related greetings",
        "vocab_count": 22,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 7,
        "title": "Home & Environment",
        "subtitle": "The world around you",
        "icon": "home",
        "description": "House, rooms, door, bed, table, chair, kitchen, farm/shamba, fire, water, common animals, trees, mountains, rivers — especially culturally significant nature words",
        "vocab_count": 24,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 8,
        "title": "Community & Daily Life",
        "subtitle": "Navigate your world with confidence",
        "icon": "storefront",
        "description": "Market, school, church/mosque, hospital, road, transport, money, work, buying and selling, I am going to, I am coming from, common community roles",
        "vocab_count": 22,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 9,
        "title": "Feelings & Emotions",
        "subtitle": "Express the fullness of your heart",
        "icon": "emoji_emotions",
        "description": "Happy, sad, angry, afraid, surprised, I like/love, I don't like, I miss you, I am proud, I am grateful, expressions of affection for family, emotional idioms",
        "vocab_count": 18,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
    {
        "order": 10,
        "title": "Everyday Verbs",
        "subtitle": "The actions of a full life",
        "icon": "directions_walk",
        "description": "Go, come, eat, drink, sleep, wake up, sit, stand, run, speak, hear, see, give, take, help, ask, answer, work, play, laugh, cry, pray",
        "vocab_count": 25,
        "lesson_type_mix": ["reading", "quiz", "quiz", "quiz"],
    },
    {
        "order": 11,
        "title": "Proverbs & Wisdom",
        "subtitle": "The heartbeat of the language",
        "icon": "history_edu",
        "description": "8 key proverbs with meanings and cultural context, common blessings, expressions of respect for elders, words of encouragement, traditional greetings between specific relationships",
        "vocab_count": 10,
        "lesson_type_mix": ["reading", "reading", "quiz"],
    },
    {
        "order": 12,
        "title": "Real Conversations",
        "subtitle": "Put it all together",
        "icon": "forum",
        "description": "Short dialogues combining all previous units: meeting a stranger, a family gathering, visiting a market, asking for directions, a phone call home, a celebration",
        "vocab_count": 15,
        "lesson_type_mix": ["reading", "quiz", "quiz"],
    },
]

LANGUAGES = {
    "kikuyu":   {"code": "ki",  "name": "Kikuyu",   "country": "Kenya", "notes": "Use correct Kikuyu orthography with circumflexes (ĩ, ũ, ĩ). Include Gikuyu-Mumbi cultural references. Greetings vary by region (Muranga vs Nyeri). Taboo: never speak ill of someone's mother."},
    "swahili":  {"code": "sw",  "name": "Swahili",  "country": "East Africa", "notes": "Standard Swahili (KiSanifu). Include coastal/inland variants where relevant. Note Arabic loanwords in vocabulary."},
    "yoruba":   {"code": "yo",  "name": "Yoruba",   "country": "Nigeria", "notes": "Include tone marks (ẹ, ọ, ṣ). Greetings are very elaborate and time-sensitive. Include prostration (ìdobalè) cultural context."},
    "zulu":     {"code": "zu",  "name": "Zulu",     "country": "South Africa", "notes": "Include click consonants (c, q, x) with pronunciation guides. Ubuntu philosophy relevant in community unit."},
    "amharic":  {"code": "am",  "name": "Amharic",  "country": "Ethiopia", "notes": "Romanize Ge'ez script (add the actual Ethiopic script in parentheses where possible). Include Orthodox Christian cultural context where relevant."},
    "luo":      {"code": "luo", "name": "Luo",      "country": "Kenya", "notes": "Nilotic language. Include fishing/Lake Victoria cultural references. Note differences from Bantu languages."},
    "kalenjin": {"code": "kln", "name": "Kalenjin", "country": "Kenya", "notes": "Nandi dialect as base. Include athletics/running cultural references. Note click sounds."},
    "kamba":    {"code": "kam", "name": "Kamba",    "country": "Kenya", "notes": "Bantu language. Include woodcarving cultural heritage. Eastern Kenya references."},
    "meru":     {"code": "mer", "name": "Meru",     "country": "Kenya", "notes": "Bantu language spoken around Mount Kenya. Related to Kikuyu but distinct. Include Mount Kenya spiritual references."},
    "luhya":    {"code": "luy", "name": "Luhya",    "country": "Kenya", "notes": "Use Lubukusu as the base dialect (largest). Western Kenya context. Include sugarcane farming cultural references."},
    "igbo":     {"code": "ig",  "name": "Igbo",     "country": "Nigeria", "notes": "Include tone marks. Odinani traditional religion context for proverbs unit. Note Igbo-Ukwu cultural history."},
    "hausa":    {"code": "ha",  "name": "Hausa",    "country": "West Africa", "notes": "Include Arabic script romanization where helpful. Islamic cultural context common. Widely spoken as trade language."},
    "shona":    {"code": "sn",  "name": "Shona",    "country": "Zimbabwe", "notes": "Karanga dialect as base. Include Great Zimbabwe historical references. Chimurenga cultural context."},
    "twi":      {"code": "tw",  "name": "Twi",      "country": "Ghana", "notes": "Asante Twi as base. Include Adinkra symbol cultural references. Note tone system."},
}

def make_id(language, unit_order, lesson_order, suffix=""):
    base = f"{language}-u{unit_order}-l{lesson_order}{suffix}"
    return base

def generate_unit_content(language_id: str, lang_info: dict, unit: dict) -> str:
    """Call Claude API to generate structured lesson content for one unit."""

    prompt = f"""You are a native speaker and language educator for {lang_info['name']} ({lang_info['country']}).
Generate structured lesson content for a language learning app called Vernaculearn.

Language notes: {lang_info['notes']}

Unit: {unit['title']} — {unit['description']}
Generate content for {unit['vocab_count']} vocabulary items.

Return ONLY valid JSON in this exact structure:
{{
  "reading_intro": "A 150-200 word introduction text in English that teaches the cultural context of this unit topic for {lang_info['name']} speakers. Make it warm, specific, and culturally authentic. Include 1-2 actual {lang_info['name']} phrases woven naturally into the text.",
  "vocabulary": [
    {{
      "native": "word or phrase in {lang_info['name']}",
      "english": "English translation",
      "pronunciation": "simple phonetic guide for English speakers",
      "example_sentence_native": "a short example sentence in {lang_info['name']}",
      "example_sentence_english": "English translation of the example sentence",
      "cultural_note": "one sentence of cultural context if relevant, otherwise null"
    }}
  ],
  "cultural_note_title": "A short title for a cultural note shown after completing this unit",
  "cultural_note_body": "A 80-120 word cultural note about this topic in {lang_info['name']} culture — proverb, tradition, history, or insight.",
  "proverb": "A {lang_info['name']} proverb related to this unit topic (if applicable), with its English meaning. Format: 'proverb — meaning'. If none fits naturally, return null."
}}

Ensure all {lang_info['name']} text uses correct orthography including diacritics. Be accurate — this content will be taught to real learners."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


def build_quiz_questions(vocab: list, lesson_index: int) -> list:
    """Convert vocabulary items into quiz questions with distractors."""
    questions = []
    # Take a slice of vocab for this lesson
    chunk_size = min(8, len(vocab))
    start = (lesson_index * chunk_size) % len(vocab)
    items = vocab[start:start + chunk_size]
    if len(items) < 3:
        items = vocab[:chunk_size]

    for i, item in enumerate(items):
        # Generate distractors from other vocab items
        others = [v for v in vocab if v["native"] != item["native"]]
        distractors = random.sample(others, min(2, len(others)))
        distractor_texts = [d["english"] for d in distractors]

        # Pad with generic distractors if needed
        while len(distractor_texts) < 2:
            distractor_texts.append(random.choice(["forest", "morning", "water", "family", "thank you", "goodbye", "house", "food"]))

        options_raw = [item["english"]] + distractor_texts[:2]
        random.shuffle(options_raw)

        correct_id = None
        options = []
        for j, opt in enumerate(options_raw):
            oid = chr(97 + j)
            options.append({"id": oid, "text": opt})
            if opt == item["english"]:
                correct_id = oid

        q = {
            "id": f"q{i+1}",
            "type": "translate",
            "prompt": item["native"],
            "native_text": item["pronunciation"],
            "options": options,
            "correct_answer_id": correct_id,
            "audio_url": None,
            "image_url": None,
        }
        questions.append(q)

    return questions


def build_vocab_flashcard_questions(vocab: list) -> list:
    """Build vocabulary card 'questions' for reading lessons — used as display items."""
    return [
        {
            "id": f"v{i+1}",
            "type": "translate",
            "prompt": item["native"],
            "native_text": item["english"],
            "options": [],
            "correct_answer_id": "",
            "audio_url": None,
            "image_url": None,
        }
        for i, item in enumerate(vocab[:12])  # Show max 12 vocab cards in reading lesson
    ]


async def seed_language(language_id: str, db):
    lang_info = LANGUAGES[language_id]
    print(f"\n🌍 Generating content for {lang_info['name']}...")

    for unit_data in UNITS:
        unit_order = unit_data["order"]
        unit_id = f"{language_id}-unit-{unit_order}"

        # Generate content via Claude API
        print(f"  📡 Unit {unit_order}: {unit_data['title']}...", end=" ", flush=True)
        try:
            content = generate_unit_content(language_id, lang_info, unit_data)
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
            continue

        time.sleep(0.5)  # Rate limit

        vocab = content.get("vocabulary", [])
        reading_intro = content.get("reading_intro", "")
        cultural_note_title = content.get("cultural_note_title")
        cultural_note_body = content.get("cultural_note_body")

        # Upsert the unit
        unit_doc = {
            "id": unit_id,
            "language_id": language_id,
            "title": unit_data["title"],
            "subtitle": unit_data["subtitle"],
            "icon": unit_data["icon"],
            "order": unit_order,
            "source": "generated",
            "status": "published",
        }
        await db.units.update_one({"id": unit_id}, {"$set": unit_doc}, upsert=True)

        # Build lessons from lesson_type_mix
        for lesson_idx, lesson_type in enumerate(unit_data["lesson_type_mix"]):
            lesson_order = lesson_idx + 1
            lesson_id = make_id(language_id, unit_order, lesson_order)

            if lesson_type == "reading":
                # Reading lesson — text intro + vocab cards
                lesson_doc = {
                    "id": lesson_id,
                    "unit_id": unit_id,
                    "language_id": language_id,
                    "title": f"{unit_data['title']} — Introduction",
                    "description": f"Read and absorb key concepts before practising",
                    "order": lesson_order,
                    "xp_reward": 10,
                    "lesson_type": "reading",
                    "reading_content": reading_intro,
                    "questions": build_vocab_flashcard_questions(vocab),
                    "status": "published",
                    "source": "generated",
                    "cultural_note": cultural_note_body if lesson_order == len(unit_data["lesson_type_mix"]) else None,
                    "cultural_note_title": cultural_note_title if lesson_order == len(unit_data["lesson_type_mix"]) else None,
                }
            else:
                # Quiz lesson
                lesson_doc = {
                    "id": lesson_id,
                    "unit_id": unit_id,
                    "language_id": language_id,
                    "title": f"{unit_data['title']} — Practice {lesson_order - 1}",
                    "description": f"Test your {unit_data['title'].lower()} vocabulary",
                    "order": lesson_order,
                    "xp_reward": 15,
                    "lesson_type": "quiz",
                    "reading_content": None,
                    "questions": build_quiz_questions(vocab, lesson_idx),
                    "status": "published",
                    "source": "generated",
                    "cultural_note": cultural_note_body if lesson_order == len(unit_data["lesson_type_mix"]) else None,
                    "cultural_note_title": cultural_note_title if lesson_order == len(unit_data["lesson_type_mix"]) else None,
                }

            await db.lessons.update_one({"id": lesson_id}, {"$set": lesson_doc}, upsert=True)

        # Insert cultural note into cultural_notes collection
        if cultural_note_body:
            note_doc = {
                "id": f"{language_id}-cn-unit{unit_order}",
                "language_id": language_id,
                "title": cultural_note_title or f"{unit_data['title']} — Cultural Note",
                "body": cultural_note_body,
                "category": "tradition" if unit_order != 11 else "proverb",
                "related_unit_ids": [unit_id],
                "source": "generated",
                "status": "published",
            }
            await db.cultural_notes.update_one({"id": note_doc["id"]}, {"$set": note_doc}, upsert=True)

    print(f"  ✅ {lang_info['name']} complete — {len(UNITS)} units, {sum(len(u['lesson_type_mix']) for u in UNITS)} lessons")


async def main(args):
    mongo = AsyncIOMotorClient(MONGODB_URI)
    db = mongo[DB_NAME]

    if args.all:
        targets = list(LANGUAGES.keys())
    elif args.priority:
        targets = ["kikuyu", "swahili"]
    elif args.language:
        if args.language not in LANGUAGES:
            print(f"Unknown language: {args.language}. Available: {', '.join(LANGUAGES.keys())}")
            return
        targets = [args.language]
    else:
        targets = ["kikuyu", "swahili"]

    print(f"🚀 Generating content for: {', '.join(targets)}")
    for lang in targets:
        await seed_language(lang, db)

    # Summary
    units = await db.units.count_documents({"source": "generated"})
    lessons = await db.lessons.count_documents({"source": "generated"})
    print(f"\n✅ Done! {units} units and {lessons} lessons in database.")
    mongo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", "-l", help="Single language to generate")
    parser.add_argument("--priority", action="store_true", help="Kikuyu + Swahili only")
    parser.add_argument("--all", action="store_true", help="All 14 languages")
    asyncio.run(main(parser.parse_args()))
```

## PART 3: RUN ORDER

After creating both files, run in this sequence:

**Step 1** — Add ANTHROPIC_API_KEY to `backend/.env`:
```
ANTHROPIC_API_KEY=your_key_here
```

**Step 2** — Install the anthropic Python SDK:
```bash
cd backend && pip install anthropic --break-system-packages
```

**Step 3** — Generate priority content first (Kikuyu + Swahili):
```bash
cd backend && python generate_content.py --priority
```

**Step 4** — Verify it worked:
```bash
python -c "
import pymongo
db = pymongo.MongoClient()['vernaculearn']
print('Units:', db.units.count_documents({'source': 'generated'}))
print('Lessons:', db.lessons.count_documents({'source': 'generated'}))
langs = list(db.units.distinct('language_id', {'source': 'generated'}))
print('Languages covered:', langs)
"
```

**Step 5** — If Step 3 looks good, run all languages:
```bash
python generate_content.py --all
```

**Step 6** — Re-run seed to ensure language entries are in DB with correct region fields:
```bash
python seed.py
```

## PART 4: DASHBOARD — SHOW LESSON TYPES DIFFERENTLY

In `frontend/src/views/DashboardView.vue`, the lesson nodes should indicate whether a lesson is a reading or quiz lesson. Update the lesson node rendering:

For completed lessons: show check icon as before
For current reading lesson: show `menu_book` icon instead of `chat_bubble`, with a teal "READ" badge instead of amber "NOW"
For current quiz lesson: keep existing `chat_bubble` icon with amber "NOW" badge
For locked lessons: show `menu_book` or `quiz` icon based on `lesson.lesson_type`

The `lesson` objects returned by `GET /api/languages/{id}/units` already include the lesson metadata (excluding questions), so `lesson.lesson_type` should be available. If it's not being returned, update the units endpoint projection to include `lesson_type`.

## PART 5: ENSURE lesson_type IS RETURNED BY THE API

In `backend/routes/lessons.py`, the units endpoint uses `{"questions": 0}` projection to exclude questions. Add `lesson_type` explicitly to ensure it's included:

The current projection `{"questions": 0}` excludes only questions and includes everything else — so `lesson_type` should already come through. But verify by checking the response from `/api/languages/kikuyu/units` after seeding. If `lesson_type` is missing, change the projection to explicitly include needed fields.

## NOTES

- The script uses `claude-sonnet-4-20250514` (Sonnet 4) for content generation — good balance of quality and speed
- Each language × 12 units = 12 API calls per language. All 14 languages = 168 API calls. At ~2000 tokens per call, that's ~336K tokens total — well within a Pro session
- The `time.sleep(0.5)` between units prevents rate limiting
- All generated content gets `source: "generated"` and `status: "published"` — it goes live immediately since it's Claude-generated (high quality baseline), not scraped
- Run `--priority` first, verify quality, then `--all`
- The reading intro text in the script is in English — if you want native language reading material, change the prompt to generate it in {language_name} with English subtitles. For now English intros with native vocabulary cards is the right approach for beginners