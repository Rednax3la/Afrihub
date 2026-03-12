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

from auth import hash_password

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")

LANGUAGES = [
    {
        "id": "yoruba",
        "name": "Yoruba",
        "code": "yo",
        "country": "Nigeria",
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
        "flag_emoji": "🇪🇹",
        "color": "red",
        "speaker_count": "32 million",
        "description": "A Semitic language and the official language of Ethiopia, written in Ge'ez script.",
        "is_free": False,
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
    # Yoruba - Unit 1
    {
        "id": "yoruba-u1-l1",
        "unit_id": "yoruba-unit-1",
        "language_id": "yoruba",
        "title": "Essentials",
        "description": "Core greetings every speaker knows",
        "order": 1,
        "xp_reward": 15,
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
        ],
    },
    # Swahili - Unit 1
    {
        "id": "swahili-u1-l1",
        "unit_id": "swahili-unit-1",
        "language_id": "swahili",
        "title": "Mambo! (Hello!)",
        "description": "Your first Swahili words",
        "order": 1,
        "xp_reward": 15,
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
        ],
    },
]

USERS = [
    {
        "name": "Admin",
        "email": "admin@vernaculearn.com",
        "password_hash": None,  # will be set via hash_password
        "role": "admin",
        "xp": 0,
        "streak": 0,
        "badges": 0,
        "avatar_url": None,
        "is_premium": True,
        "active_languages": [],
        "created_at": datetime.utcnow(),
    },
    {
        "name": "Amara Okafor",
        "email": "amara@vernaculearn.com",
        "password_hash": None,
        "role": "tutor",
        "tutor_status": "active",
        "bio": "Native Yoruba speaker from Lagos. Language educator with 8 years of experience teaching vernacular languages to diaspora learners.",
        "languages_taught": ["yoruba"],
        "voice_character": "Amara",
        "location": "Lagos, Nigeria",
        "xp": 0,
        "streak": 0,
        "badges": 0,
        "avatar_url": None,
        "is_premium": False,
        "active_languages": [],
        "created_at": datetime.utcnow(),
    },
    {
        "name": "Juma Mwangi",
        "email": "juma@vernaculearn.com",
        "password_hash": None,
        "role": "tutor",
        "tutor_status": "active",
        "bio": "Nairobi-born linguist and Swahili language advocate. Passionate about preserving East African language heritage.",
        "languages_taught": ["swahili"],
        "voice_character": "Juma",
        "location": "Nairobi, Kenya",
        "xp": 0,
        "streak": 0,
        "badges": 0,
        "avatar_url": None,
        "is_premium": False,
        "active_languages": [],
        "created_at": datetime.utcnow(),
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

    # Clear existing data
    await db.languages.drop()
    await db.units.drop()
    await db.lessons.drop()

    await db.languages.insert_many(LANGUAGES)
    print(f"✅ Inserted {len(LANGUAGES)} languages")

    await db.units.insert_many(UNITS)
    print(f"✅ Inserted {len(UNITS)} units")

    await db.lessons.insert_many(LESSONS)
    print(f"✅ Inserted {len(LESSONS)} lessons")

    # Set password hashes
    for u in USERS:
        if u["name"] == "Admin":
            u["password_hash"] = hash_password("Admin1234!")
        elif u["name"] == "Amara Okafor":
            u["password_hash"] = hash_password("Tutor1234!")
        elif u["name"] == "Juma Mwangi":
            u["password_hash"] = hash_password("Tutor1234!")

    # Seed users (don't drop — just upsert by email)
    for u in USERS:
        await db.users.update_one(
            {"email": u["email"]},
            {"$set": u},
            upsert=True,
        )
    print(f"✅ Upserted {len(USERS)} seed users (admin + tutors)")

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.progress.create_index([("user_id", 1), ("lesson_id", 1)], unique=True)

    print("\n🌍 Vernaculearn database seeded successfully!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
