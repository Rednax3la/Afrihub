import logging
import os
import re
import time
from contextlib import contextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")

client: AsyncIOMotorClient = None
db = None

# Tracks the outcome of the most recent connection attempt so other parts of
# the app (e.g. the root health endpoint) can report accurate status.
connection_status = {"connected": False, "error": None}


def _mask_uri(uri: str) -> str:
    """Mask the password in a MongoDB connection string before logging it."""
    return re.sub(r"://([^:/@]+):([^@]+)@", r"://\1:****@", uri)


async def connect_db():
    global client, db

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI environment variable is not set. "
            "Set it to your Railway MongoDB service's connection string, e.g. by "
            "referencing ${{MongoDB.MONGO_URL}} in this service's variables."
        )

    print(f"🔗 Connecting to MongoDB using URI: {_mask_uri(MONGODB_URI)}")

    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[DB_NAME]
        # Force an actual round-trip so connection failures surface immediately
        # instead of only on first use.
        await client.admin.command("ping")
        connection_status["connected"] = True
        connection_status["error"] = None
        print(f"✅ Connected to MongoDB: {DB_NAME}")
        await ensure_indexes()
    except Exception as e:
        connection_status["connected"] = False
        connection_status["error"] = str(e)
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


@contextmanager
def log_timing(label: str):
    """Log how long the wrapped block took, in milliseconds."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("⏱️  %s took %.1f ms", label, elapsed_ms)
        print(f"⏱️  {label} took {elapsed_ms:.1f} ms")


# (collection, keys, options)
_INDEXES = [
    # Lessons: the unit_id indexes back the actual query paths; the language_id
    # index covers lessons that carry a denormalised language_id.
    ("lessons", [("language_id", 1), ("status", 1)], {}),
    ("lessons", [("unit_id", 1), ("status", 1), ("order", 1)], {}),
    ("lessons", [("id", 1)], {}),
    # Units
    ("units", [("language_id", 1)], {}),
    ("units", [("language_id", 1), ("order", 1)], {}),
    ("units", [("id", 1)], {}),
    # Languages
    ("languages", [("id", 1)], {}),
    # Progress (unique, matches the index created by seed.py)
    ("progress", [("user_id", 1), ("lesson_id", 1)], {"unique": True}),
]


async def ensure_indexes():
    """Create indexes so hot queries use index scans instead of collection scans.

    Index creation is idempotent. Failures are logged and never block startup.
    """
    start = time.perf_counter()
    for collection, keys, options in _INDEXES:
        try:
            await db[collection].create_index(keys, **options)
        except Exception as e:
            logger.warning("Could not create index on %s %s: %s", collection, keys, e)
            print(f"⚠️  Could not create index on {collection} {keys}: {e}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"📇 Ensured MongoDB indexes in {elapsed_ms:.1f} ms")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed.")


def get_db():
    return db


def get_connection_status():
    return connection_status
