"""
Run this once to seed the database with sample data:
    python seed.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
print("MONGODB_URI = ", os.getenv("MONGODB_URI"))  # a check on whether the env is properly loaded.

from auth import hash_password

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")

LANGUAGES = [
    {
        "id": "yoruba",
        "name": "Yoruba",
        "code": "yo",
        "country": "Nigeria",
        "region": "West Africa",
        "flag_emoji": "🇳🇬",
        "color": "emerald",
        "speaker_count": "47 million",
        "description": "Spoken in southwestern Nigeria and neighbouring Benin and Togo. Rich in tone and proverb.",
        "is_free": True,
    },
    {
        "id": "swahili",
        "name": "Swahili",
        "code": "sw",
        "country": "East Africa",
        "region": "East Africa",
        "flag_emoji": "🌍",
        "color": "blue",
        "speaker_count": "200 million",
        "description": "A Bantu language spoken across East Africa. The lingua franca of the African Union.",
        "is_free": True,
    },
    {
        "id": "zulu",
        "name": "Zulu",
        "code": "zu",
        "country": "South Africa",
        "region": "Southern Africa",
        "flag_emoji": "🇿🇦",
        "color": "amber",
        "speaker_count": "12 million",
        "description": "A Nguni Bantu language and one of South Africa's 11 official languages.",
        "is_free": False,
    },
    {
        "id": "amharic",
        "name": "Amharic",
        "code": "am",
        "country": "Ethiopia",
        "region": "East Africa",
        "flag_emoji": "🇪🇹",
        "color": "red",
        "speaker_count": "32 million",
        "description": "A Semitic language and the official language of Ethiopia, written in Ge'ez script.",
        "is_free": False,
    },
    {
        "id": "kikuyu",
        "name": "Kikuyu",
        "code": "ki",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "purple",
        "speaker_count": "8 million",
        "description": "The language of the Agĩkũyũ people, spoken mainly in central Kenya around Mount Kenya.",
        "is_free": True,
    },
    {
        "id": "luo",
        "name": "Luo",
        "code": "luo",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "pink",
        "speaker_count": "6 million",
        "description": "A Nilotic language spoken by the Luo people around Lake Victoria in western Kenya.",
        "is_free": True,
    },
    {
        "id": "kalenjin",
        "name": "Kalenjin",
        "code": "kln",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "orange",
        "speaker_count": "5 million",
        "description": "A group of related dialects spoken by the Kalenjin people in Kenya's Rift Valley Province.",
        "is_free": True,
    },
    {
        "id": "kamba",
        "name": "Kamba",
        "code": "kam",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "teal",
        "speaker_count": "4 million",
        "description": "A Bantu language spoken by the Akamba people in eastern Kenya, especially Machakos and Kitui.",
        "is_free": True,
    },
    {
        "id": "meru",
        "name": "Meru",
        "code": "mer",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "cyan",
        "speaker_count": "2 million",
        "description": "A Bantu language of the Ameru people living on the northeastern slopes of Mount Kenya.",
        "is_free": True,
    },
    {
        "id": "luhya",
        "name": "Luhya",
        "code": "luy",
        "country": "Kenya",
        "region": "East Africa",
        "flag_emoji": "🇰🇪",
        "color": "indigo",
        "speaker_count": "7 million",
        "description": "A cluster of Bantu languages spoken by the Luhya people in western Kenya.",
        "is_free": True,
    },
]

UNITS = [
    # Yoruba
    {
        "id": "yoruba-unit-1",
        "language_id": "yoruba",
        "title": "The Basics",
        "subtitle": "Greetings & Everyday Phrases",
        "icon": "waving_hand",
        "order": 1,
    },
    {
        "id": "yoruba-unit-2",
        "language_id": "yoruba",
        "title": "Common Nouns",
        "subtitle": "People, Places, Things",
        "icon": "category",
        "order": 2,
    },
    # Swahili
    {
        "id": "swahili-unit-1",
        "language_id": "swahili",
        "title": "Karibu! (Welcome!)",
        "subtitle": "First Words & Greetings",
        "icon": "waving_hand",
        "order": 1,
    },
]

LESSONS = [
    # ── Yoruba - Unit 1 ──────────────────────────────────────────────────────
    {
        "id": "yoruba-u1-l1",
        "unit_id": "yoruba-unit-1",
        "language_id": "yoruba",
        "title": "Essentials",
        "description": "Core greetings every speaker knows",
        "order": 1,
        "xp_reward": 15,
        "status": "published",
        "cultural_note_title": "Greetings Reflect Respect",
        "cultural_note": (
            "In Yoruba culture, greetings are deeply tied to time of day and the social relationship "
            "between speakers. Juniors are expected to prostrate (males) or kneel (females) when "
            "greeting elders — a practice called 'ìdobalè'. The phrase 'Ẹ káàárọ̀' is reserved "
            "for mornings, while 'Ẹ káàbọ̀' means 'welcome home'. Using the right greeting at the "
            "right moment signals cultural awareness and earns deep respect."
        ),
        "questions": [
            {
                "id": "q1",
                "type": "translate",
                "prompt": "Ẹ káàárọ̀, ṣé dáadáa ni o wà?",
                "native_text": "Good morning, how are you?",
                "options": [
                    {"id": "a", "text": "Good morning, how are you?"},
                    {"id": "b", "text": "Welcome home, friend."},
                    {"id": "c", "text": "Good night, sleep well."},
                ],
                "correct_answer_id": "a",
            },
            {
                "id": "q2",
                "type": "translate",
                "prompt": "E kaabo",
                "native_text": "Welcome",
                "options": [
                    {"id": "a", "text": "Goodbye"},
                    {"id": "b", "text": "Welcome"},
                    {"id": "c", "text": "Thank you"},
                ],
                "correct_answer_id": "b",
            },
            {
                "id": "q3",
                "type": "multiple_choice",
                "prompt": "How do you say 'Thank you' in Yoruba?",
                "native_text": None,
                "options": [
                    {"id": "a", "text": "Pẹlẹ o"},
                    {"id": "b", "text": "E kaabo"},
                    {"id": "c", "text": "E ṣeun"},
                ],
                "correct_answer_id": "c",
            },
            {
                "id": "q4",
                "type": "listen",
                "prompt": "Listen and choose what you hear",
                "native_text": None,
                "audio_url": None,  # placeholder — tutor will upload real audio
                "options": [
                    {"id": "a", "text": "Ẹ káàárọ̀ (Good morning)"},
                    {"id": "b", "text": "Ẹ káàlẹ̀ (Good evening)"},
                    {"id": "c", "text": "Ẹ káàbọ̀ (Welcome home)"},
                ],
                "correct_answer_id": "a",
            },
        ],
    },
    {
        "id": "yoruba-u1-l2",
        "unit_id": "yoruba-unit-1",
        "language_id": "yoruba",
        "title": "Common Nouns",
        "description": "Everyday objects and people",
        "order": 2,
        "xp_reward": 15,
        "status": "published",
        "questions": [
            {
                "id": "q1",
                "type": "translate",
                "prompt": "Omi",
                "native_text": "Water",
                "options": [
                    {"id": "a", "text": "Food"},
                    {"id": "b", "text": "Water"},
                    {"id": "c", "text": "Fire"},
                ],
                "correct_answer_id": "b",
            },
            {
                "id": "q2",
                "type": "translate",
                "prompt": "Ìdílé",
                "native_text": "Family",
                "options": [
                    {"id": "a", "text": "Market"},
                    {"id": "b", "text": "House"},
                    {"id": "c", "text": "Family"},
                ],
                "correct_answer_id": "c",
            },
            {
                "id": "q3",
                "type": "image",
                "prompt": "What does this image show?",
                "native_text": None,
                "image_url": None,  # placeholder — tutor will upload
                "options": [
                    {"id": "a", "text": "Omi (Water)"},
                    {"id": "b", "text": "Ina (Fire)"},
                    {"id": "c", "text": "Ilẹ̀ (Ground)"},
                ],
                "correct_answer_id": "a",
            },
        ],
    },
    # ── Swahili - Unit 1 ─────────────────────────────────────────────────────
    {
        "id": "swahili-u1-l1",
        "unit_id": "swahili-unit-1",
        "language_id": "swahili",
        "title": "Mambo! (Hello!)",
        "description": "Your first Swahili words",
        "order": 1,
        "xp_reward": 15,
        "status": "published",
        "cultural_note_title": "Mambo / Poa — The Street Greeting",
        "cultural_note": (
            "In Kenya and Tanzania, the call-and-response 'Mambo? / Poa!' is the informal equivalent "
            "of 'What's up? / Cool!' It's a mark of belonging — especially in youth culture and urban "
            "areas like Nairobi. Formal Swahili uses 'Habari?' (What news?) with replies like 'Nzuri' "
            "(Good) or 'Salama' (Peaceful). Using 'Mambo' with an elder can sound too casual, so "
            "reading the social context is key."
        ),
        "questions": [
            {
                "id": "q1",
                "type": "translate",
                "prompt": "Habari yako?",
                "native_text": "How are you?",
                "options": [
                    {"id": "a", "text": "Where are you going?"},
                    {"id": "b", "text": "How are you?"},
                    {"id": "c", "text": "What is your name?"},
                ],
                "correct_answer_id": "b",
            },
            {
                "id": "q2",
                "type": "multiple_choice",
                "prompt": "How do you say 'Good' (as a reply to how are you) in Swahili?",
                "native_text": None,
                "options": [
                    {"id": "a", "text": "Nzuri"},
                    {"id": "b", "text": "Asante"},
                    {"id": "c", "text": "Karibu"},
                ],
                "correct_answer_id": "a",
            },
            {
                "id": "q3",
                "type": "listen",
                "prompt": "Listen and choose what you hear",
                "native_text": None,
                "audio_url": None,  # placeholder
                "options": [
                    {"id": "a", "text": "Habari (News / How are you)"},
                    {"id": "b", "text": "Asante (Thank you)"},
                    {"id": "c", "text": "Karibu (Welcome)"},
                ],
                "correct_answer_id": "c",
            },
            {
                "id": "q4",
                "type": "video",
                "prompt": "Watch the greeting demonstration, then answer: What gesture accompanies 'Shikamoo' when greeting an elder?",
                "native_text": None,
                "video_url": None,  # placeholder — tutor will upload
                "options": [
                    {"id": "a", "text": "A handshake with both hands"},
                    {"id": "b", "text": "Bowing the head slightly"},
                    {"id": "c", "text": "Waving from a distance"},
                ],
                "correct_answer_id": "b",
            },
        ],
    },
]

# Temporary shared password for every seeded tutor account.
MOCK_TUTOR_PASSWORD = "Tutor1234!"
ADMIN_PASSWORD = "Admin1234!"
# Mock/seed accounts all live on this domain.
MOCK_DOMAIN = "vernaculearn.com"


def mock_tutor(
    *, name, email, languages_taught, bio="", voice_character=None, location=None
) -> dict:
    """Build a seed tutor.

    Every seed tutor goes through this one helper. Previously each tutor was
    written out by hand and the password hash was applied by a name-gated
    `if` in seed(), so any tutor added later was inserted with
    password_hash=None and could never log in.
    """
    return {
        "name": name,
        "email": email.strip().lower(),
        "password_hash": hash_password(MOCK_TUTOR_PASSWORD),
        "role": "tutor",
        "tutor_status": "active",
        "auth_provider": "password",
        "bio": bio,
        "languages_taught": languages_taught,
        "voice_character": voice_character or name.split()[0],
        "location": location,
    }


ADMIN_USER = {
    "name": "Admin",
    "email": f"admin@{MOCK_DOMAIN}",
    "password_hash": hash_password(ADMIN_PASSWORD),
    "role": "admin",
    "auth_provider": "password",
    "is_premium": True,
}

TUTORS = [
    mock_tutor(
        name="Amara Okafor",
        email=f"amara@{MOCK_DOMAIN}",
        languages_taught=["yoruba"],
        bio="Native Yoruba speaker from Lagos. Language educator with 8 years of experience teaching vernacular languages to diaspora learners.",
        voice_character="Amara",
        location="Lagos, Nigeria",
    ),
    mock_tutor(
        name="Juma Mwangi",
        email=f"juma@{MOCK_DOMAIN}",
        languages_taught=["swahili"],
        bio="Nairobi-born linguist and Swahili language advocate. Passionate about preserving East African language heritage.",
        voice_character="Juma",
        location="Nairobi, Kenya",
    ),
    mock_tutor(
        name="Cucu Margaret",
        email=f"cucu@{MOCK_DOMAIN}",
        languages_taught=["kikuyu"],
        bio="Kikuyu elder and storyteller from Nyeri. Teaches the language the way it is spoken at home, through proverbs, songs and everyday conversation.",
        voice_character="Cucu",
        location="Nyeri, Kenya",
    ),
]

USERS = [ADMIN_USER, *TUTORS]

# Fields a reseed must never clobber on an account that already exists --
# real progress and anything an admin or the tutor has since changed.
_PRESERVE_ON_UPDATE = (
    "xp", "streak", "badges", "earned_badges", "language_xp", "last_activity_date",
    "active_languages", "avatar_url", "created_at", "session_version",
    "subscription_status", "subscription_tier", "expires_at", "admin_granted",
)

_USER_DEFAULTS = {
    "xp": 0,
    "streak": 0,
    "badges": 0,
    "avatar_url": None,
    "active_languages": [],
    "language_xp": {},
}


async def upsert_seed_user(db, user: dict) -> None:
    """Idempotent upsert: never duplicates, never overwrites earned data."""
    doc = dict(user)
    email = doc["email"].strip().lower()
    doc["email"] = email

    set_fields = {k: v for k, v in doc.items() if k not in _PRESERVE_ON_UPDATE}
    insert_only = {**_USER_DEFAULTS, "created_at": datetime.utcnow()}
    insert_only = {k: v for k, v in insert_only.items() if k not in set_fields}

    await db.users.update_one(
        {"email": email},
        {"$set": set_fields, "$setOnInsert": insert_only},
        upsert=True,
    )

BADGES = [
    {"id": "first-lesson", "name": "First Step", "description": "Complete your first lesson", "icon": "🎯", "criteria_type": "lessons_completed", "criteria_value": 1},
    {"id": "streak-7", "name": "7-Day Streak", "description": "Learn for 7 consecutive days", "icon": "🔥", "criteria_type": "streak", "criteria_value": 7},
    {"id": "xp-100", "name": "Century Club", "description": "Earn 100 XP", "icon": "⚡", "criteria_type": "xp", "criteria_value": 100},
    {"id": "lessons-10", "name": "Dedicated Learner", "description": "Complete 10 lessons", "icon": "📚", "criteria_type": "lessons_completed", "criteria_value": 10},
    {"id": "perfect-score", "name": "Perfect Score", "description": "Get 100% on any lesson", "icon": "⭐", "criteria_type": "perfect_lesson", "criteria_value": 1},
]

CULTURAL_NOTES = [
    {
        "id": "yo-cn-1",
        "language_id": "yoruba",
        "title": "The Power of Yoruba Proverbs",
        "body": (
            "Yoruba is one of the world's most proverb-rich languages. Elders say 'Òwe l'ẹṣin ọrọ̀' — "
            "'Proverbs are the horses of speech.' When direct speech fails, a well-chosen proverb carries "
            "the message. Proverbs encode centuries of wisdom about nature, human relationships, and "
            "community values."
        ),
        "category": "proverb",
        "related_unit_ids": ["yoruba-unit-1"],
        "source": "tutor",
    },
    {
        "id": "sw-cn-1",
        "language_id": "swahili",
        "title": "Swahili as a Trade Language",
        "body": (
            "Swahili evolved as a trade lingua franca along the East African coast, blending Bantu grammar "
            "with Arabic, Persian, Portuguese, and later English loanwords. 'Safari', 'Simba', and 'Hakuna "
            "Matata' are all Swahili words known worldwide. The language's openness to borrowing reflects "
            "East Africa's history as a crossroads of Indian Ocean trade."
        ),
        "category": "history",
        "related_unit_ids": ["swahili-unit-1"],
        "source": "tutor",
    },
]


async def _upsert_all(collection, docs, key="id") -> None:
    """Upsert by natural key instead of dropping the collection.

    Dropping would have destroyed tutor-authored units, lessons and notes on
    every reseed.
    """
    for doc in docs:
        payload = {k: v for k, v in doc.items() if k != "_id"}
        await collection.update_one({key: doc[key]}, {"$set": payload}, upsert=True)


async def seed_database(db) -> dict:
    """Idempotent seed. Safe to run repeatedly against a live database."""
    await _upsert_all(db.languages, LANGUAGES)
    await _upsert_all(db.units, UNITS)
    await _upsert_all(db.lessons, LESSONS)
    await _upsert_all(db.badges, BADGES)
    await _upsert_all(db.cultural_notes, CULTURAL_NOTES)

    for user in USERS:
        await upsert_seed_user(db, user)

    await db.users.create_index("email", unique=True)
    await db.progress.create_index([("user_id", 1), ("lesson_id", 1)], unique=True)
    await db.cultural_notes.create_index("language_id")
    await db.lessons.create_index([("status", 1), ("language_id", 1)])

    return {
        "languages": len(LANGUAGES),
        "units": len(UNITS),
        "lessons": len(LESSONS),
        "badges": len(BADGES),
        "cultural_notes": len(CULTURAL_NOTES),
        "users": len(USERS),
    }


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    counts = await seed_database(db)

    for name, count in counts.items():
        print(f"✅ Upserted {count} {name.replace('_', ' ')}")

    print("\n🌍 Vernaculearn database seeded successfully!")
    print(f"   Admin: {ADMIN_USER['email']}  /  {ADMIN_PASSWORD}")
    for tutor in TUTORS:
        print(f"   Tutor: {tutor['email']:<28}  /  {MOCK_TUTOR_PASSWORD}  ({tutor['name']})")
    print(f"\n   ⚠️  {MOCK_TUTOR_PASSWORD} is a temporary shared password for mock tutor accounts.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
