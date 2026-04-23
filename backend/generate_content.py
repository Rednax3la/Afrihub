"""
Vernaculearn Content Generator
Generates structured lesson content for all 14 languages using Claude API.

Usage:
    python generate_content.py --language kikuyu
    python generate_content.py --priority      (Kikuyu + Swahili only)
    python generate_content.py --all           (all 14 languages)
"""

import anthropic
import asyncio
import json
import os
import time
import argparse
import random
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
    "kikuyu":   {"code": "ki",  "name": "Kikuyu",   "country": "Kenya",        "region": "East Africa",    "notes": "Use correct Kikuyu orthography with circumflexes (ĩ, ũ). Include Gikuyu-Mumbi cultural references. Greetings vary by region (Muranga vs Nyeri)."},
    "swahili":  {"code": "sw",  "name": "Swahili",  "country": "East Africa",  "region": "East Africa",    "notes": "Standard Swahili (KiSanifu). Include coastal/inland variants where relevant. Note Arabic loanwords."},
    "yoruba":   {"code": "yo",  "name": "Yoruba",   "country": "Nigeria",      "region": "West Africa",    "notes": "Include tone marks (ẹ, ọ, ṣ). Greetings are elaborate and time-sensitive. Include prostration (ìdobalè) cultural context."},
    "zulu":     {"code": "zu",  "name": "Zulu",     "country": "South Africa", "region": "Southern Africa","notes": "Include click consonants (c, q, x) with pronunciation guides. Ubuntu philosophy relevant in community unit."},
    "amharic":  {"code": "am",  "name": "Amharic",  "country": "Ethiopia",     "region": "East Africa",    "notes": "Romanize Ge'ez script. Include Orthodox Christian cultural context where relevant."},
    "luo":      {"code": "luo", "name": "Luo",      "country": "Kenya",        "region": "East Africa",    "notes": "Nilotic language. Include fishing/Lake Victoria cultural references."},
    "kalenjin": {"code": "kln", "name": "Kalenjin", "country": "Kenya",        "region": "East Africa",    "notes": "Nandi dialect as base. Include athletics/running cultural references."},
    "kamba":    {"code": "kam", "name": "Kamba",    "country": "Kenya",        "region": "East Africa",    "notes": "Bantu language. Include woodcarving cultural heritage. Eastern Kenya references."},
    "meru":     {"code": "mer", "name": "Meru",     "country": "Kenya",        "region": "East Africa",    "notes": "Bantu language spoken around Mount Kenya. Include Mount Kenya spiritual references."},
    "luhya":    {"code": "luy", "name": "Luhya",    "country": "Kenya",        "region": "East Africa",    "notes": "Use Lubukusu as the base dialect. Western Kenya context. Include sugarcane farming references."},
    "igbo":     {"code": "ig",  "name": "Igbo",     "country": "Nigeria",      "region": "West Africa",    "notes": "Include tone marks. Odinani traditional religion context for proverbs unit."},
    "hausa":    {"code": "ha",  "name": "Hausa",    "country": "West Africa",  "region": "West Africa",    "notes": "Include Arabic script romanization where helpful. Islamic cultural context common."},
    "shona":    {"code": "sn",  "name": "Shona",    "country": "Zimbabwe",     "region": "Southern Africa","notes": "Karanga dialect as base. Include Great Zimbabwe historical references."},
    "twi":      {"code": "tw",  "name": "Twi",      "country": "Ghana",        "region": "West Africa",    "notes": "Asante Twi as base. Include Adinkra symbol cultural references."},
}


def generate_unit_content(language_id: str, lang_info: dict, unit: dict) -> dict:
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
        messages=[{"role": "user", "content": prompt}],
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
    chunk_size = min(8, len(vocab))
    start = (lesson_index * chunk_size) % max(len(vocab), 1)
    items = vocab[start:start + chunk_size]
    if len(items) < 3:
        items = vocab[:chunk_size]

    questions = []
    for i, item in enumerate(items):
        others = [v for v in vocab if v["native"] != item["native"]]
        distractors = random.sample(others, min(2, len(others)))
        distractor_texts = [d["english"] for d in distractors]

        # Pad with generic distractors if needed
        generics = ["forest", "morning", "water", "family", "thank you", "goodbye", "house", "food"]
        while len(distractor_texts) < 2:
            distractor_texts.append(random.choice(generics))

        options_raw = [item["english"]] + distractor_texts[:2]
        random.shuffle(options_raw)

        correct_id = None
        options = []
        for j, opt in enumerate(options_raw):
            oid = chr(97 + j)
            options.append({"id": oid, "text": opt})
            if opt == item["english"]:
                correct_id = oid

        questions.append({
            "id": f"q{i + 1}",
            "type": "translate",
            "prompt": item["native"],
            "native_text": item.get("pronunciation", ""),
            "options": options,
            "correct_answer_id": correct_id,
            "audio_url": None,
            "image_url": None,
        })

    return questions


def build_vocab_flashcard_questions(vocab: list) -> list:
    """Build vocabulary cards for reading lessons — displayed as visual items, not graded."""
    return [
        {
            "id": f"v{i + 1}",
            "type": "translate",
            "prompt": item["native"],
            "native_text": item.get("english", ""),
            "options": [],
            "correct_answer_id": "",
            "audio_url": None,
            "image_url": None,
        }
        for i, item in enumerate(vocab[:12])
    ]


async def seed_language(language_id: str, db):
    lang_info = LANGUAGES[language_id]
    print(f"\n🌍 Generating content for {lang_info['name']}...")

    for unit_data in UNITS:
        unit_order = unit_data["order"]
        unit_id = f"{language_id}-unit-{unit_order}"

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
        last_lesson_idx = len(unit_data["lesson_type_mix"]) - 1
        for lesson_idx, lesson_type in enumerate(unit_data["lesson_type_mix"]):
            lesson_order = lesson_idx + 1
            lesson_id = f"{language_id}-u{unit_order}-l{lesson_order}"
            is_last = lesson_idx == last_lesson_idx

            if lesson_type == "reading":
                lesson_doc = {
                    "id": lesson_id,
                    "unit_id": unit_id,
                    "language_id": language_id,
                    "title": f"{unit_data['title']} — Introduction",
                    "description": "Read and absorb key concepts before practising",
                    "order": lesson_order,
                    "xp_reward": 10,
                    "lesson_type": "reading",
                    "reading_content": reading_intro,
                    "questions": build_vocab_flashcard_questions(vocab),
                    "status": "published",
                    "source": "generated",
                    "cultural_note": cultural_note_body if is_last else None,
                    "cultural_note_title": cultural_note_title if is_last else None,
                }
            else:
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
                    "cultural_note": cultural_note_body if is_last else None,
                    "cultural_note_title": cultural_note_title if is_last else None,
                }

            await db.lessons.update_one({"id": lesson_id}, {"$set": lesson_doc}, upsert=True)

        # Insert cultural note into cultural_notes collection
        if cultural_note_body:
            note_doc = {
                "id": f"{language_id}-cn-unit{unit_order}",
                "language_id": language_id,
                "title": cultural_note_title or f"{unit_data['title']} — Cultural Note",
                "body": cultural_note_body,
                "category": "proverb" if unit_order == 11 else "tradition",
                "related_unit_ids": [unit_id],
                "source": "generated",
                "status": "published",
            }
            await db.cultural_notes.update_one(
                {"id": note_doc["id"]}, {"$set": note_doc}, upsert=True
            )

    total_lessons = sum(len(u["lesson_type_mix"]) for u in UNITS)
    print(f"  ✅ {lang_info['name']} complete — {len(UNITS)} units, {total_lessons} lessons")


async def main(args):
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not set in backend/.env")
        return

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

    units = await db.units.count_documents({"source": "generated"})
    lessons = await db.lessons.count_documents({"source": "generated"})
    print(f"\n✅ Done! {units} generated units and {lessons} generated lessons in database.")
    mongo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vernaculearn Content Generator")
    parser.add_argument("--language", "-l", help="Single language to generate (e.g. kikuyu)")
    parser.add_argument("--priority", action="store_true", help="Generate Kikuyu + Swahili only")
    parser.add_argument("--all", action="store_true", help="Generate all 14 languages")
    asyncio.run(main(parser.parse_args()))
