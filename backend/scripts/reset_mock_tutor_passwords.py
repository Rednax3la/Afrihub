"""Repair mock tutor logins.

Targets exactly the mock accounts: role == "tutor" AND an email ending in
"@vernaculearn.com". Real tutor accounts on any other domain are never touched.

For each match it sets:
  * password_hash  -> the temporary shared password (Tutor1234!)
  * tutor_status   -> "active"   (pending/suspended tutors cannot use the portal)
  * role           -> "tutor"    (normalised, in case of a stored typo)
  * auth_provider  -> "password" (so password login is not bypassed)
  * email          -> stripped + lowercased, if it was not already

    python scripts/reset_mock_tutor_passwords.py            # dry run
    python scripts/reset_mock_tutor_passwords.py --apply     # actually write
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from auth import hash_password
from seed import MOCK_DOMAIN, MOCK_TUTOR_PASSWORD

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "vernaculearn")


async def reset_mock_tutors(apply: bool) -> int:
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    changed = 0

    try:
        # Case-insensitive match so a mixed-case stored address is still caught.
        cursor = db.users.find(
            {
                "role": {"$regex": r"^\s*tutor\s*$", "$options": "i"},
                "email": {"$regex": rf"@{MOCK_DOMAIN}\s*$", "$options": "i"},
            }
        )
        async for user in cursor:
            email = (user.get("email") or "").strip().lower()
            updates = {
                "password_hash": hash_password(MOCK_TUTOR_PASSWORD),
                "tutor_status": "active",
                "role": "tutor",
                "auth_provider": "password",
                "email": email,
            }
            reasons = []
            if not user.get("password_hash"):
                reasons.append("missing password_hash")
            if user.get("tutor_status") != "active":
                reasons.append(f"tutor_status={user.get('tutor_status')!r}")
            if user.get("email") != email:
                reasons.append("email not normalised")
            if user.get("role") != "tutor":
                reasons.append(f"role={user.get('role')!r}")

            changed += 1
            detail = ", ".join(reasons) or "password reset only"
            print(f"  {email}  ({user.get('name', '?')})  -- {detail}")
            if apply:
                await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
    finally:
        client.close()

    verb = "Updated" if apply else "Would update"
    print(f"\n{verb} {changed} mock tutor account(s) on @{MOCK_DOMAIN}.")
    if not apply and changed:
        print("Dry run - nothing was written. Re-run with --apply to persist.")
    print(f"\n⚠️  {MOCK_TUTOR_PASSWORD} is a temporary shared password for mock tutor accounts.")
    print("   Rotate or disable these accounts before the platform is public.")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = parser.parse_args()
    asyncio.run(reset_mock_tutors(args.apply))
