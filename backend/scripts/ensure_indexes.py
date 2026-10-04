"""Print the planned indexes by default; explicit --apply uses owner-selected DB."""
import argparse
import asyncio
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.dictionary_data import dictionary_indexes

INDEXES = {
    'languages': [[('id', 1)]], 'users': [[('email', 1)]],
    'units': [[('id', 1)], [('language_id', 1), ('order', 1)]],
    'lessons': [[('id', 1)], [('unit_id', 1), ('status', 1), ('order', 1)]],
    # The unique (user_id, lesson_id) index is already owned by database.ensure_indexes.
    'progress': [[('user_id', 1), ('review_schedule.next_review_date', 1)]],
    'foundations': [[('language_id', 1), ('status', 1), ('order', 1)]],
}


async def run(apply):
    print({'indexes': INDEXES, 'dictionary': 'status/language + native_key/english_key prefix indexes', 'apply': apply})
    if not apply:
        return
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGODB_URI'], serverSelectionTimeoutMS=10000)
    try:
        db = client[os.environ['DB_NAME']]
        for name, indexes in INDEXES.items():
            for index in indexes:
                await db[name].create_index(index)
        await dictionary_indexes(db)
    finally:
        client.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--apply', action='store_true')
    asyncio.run(run(cli.parse_args().apply))
