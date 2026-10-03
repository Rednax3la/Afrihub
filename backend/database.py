import os
import re
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

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
    except Exception as e:
        connection_status["connected"] = False
        connection_status["error"] = str(e)
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed.")


def get_db():
    return db


def get_connection_status():
    return connection_status
