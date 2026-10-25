"""One-off migration: zero out streaks that have already lapsed.

Before the effective-streak fix, a lapsed streak kept its stale stored value
(and reset to 1, never 0, on the next completion). Reads are now corrected on
the fly by ``services.streaks.effective_streak``, but this script cleans up the
stored field so the database matches what users see.

Sets ``streak`` to 0 for every user whose ``last_activity_date`` is missing or
older than yesterday (Africa/Nairobi calendar day).

    python scripts/fix_streaks.py            # dry run, writes nothing
    python scripts/fix_streaks.py --apply    # actually update
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from services.streaks import effective_streak, to_eat_date, today_eat

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")


async def fix_streaks(apply: bool) -> int:
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    today = today_eat()

    changed = 0
    try:
        cursor = db.users.find(
            {"streak": {"$gt": 0}},
            {"email": 1, "streak": 1, "last_activity_date": 1},
        )
        async for user in cursor:
            if effective_streak(user, today) != 0:
                continue
            changed += 1
            last = to_eat_date(user.get("last_activity_date"))
            print(
                f"  {user.get('email', user['_id'])}: streak {user.get('streak')} -> 0 "
                f"(last activity: {last or 'never'})"
            )
            if apply:
                await db.users.update_one({"_id": user["_id"]}, {"$set": {"streak": 0}})
    finally:
        client.close()

    verb = "Updated" if apply else "Would update"
    print(f"\n{verb} {changed} user(s) whose streak has lapsed (today in EAT: {today}).")
    if not apply and changed:
        print("Dry run — nothing was written. Re-run with --apply to persist.")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = parser.parse_args()
    asyncio.run(fix_streaks(args.apply))
