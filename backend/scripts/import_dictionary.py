"""Dry run by default, with NO database connection. Explicit --apply for owner use."""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.dictionary_data import dictionary_indexes, import_entries


async def run(args):
    def entries():
        for path in sorted(args.directory.glob('*.jsonl')):
            if path.name.endswith('.raw.jsonl'):
                continue
            with path.open(encoding='utf-8') as stream:
                for line in stream:
                    yield json.loads(line)
    if not args.apply:
        print(await import_entries(None, entries(), publish_reviewed=args.publish_reviewed))
        return
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGODB_URI'], serverSelectionTimeoutMS=10000)
    try:
        db = client[os.environ['DB_NAME']]
        await dictionary_indexes(db)
        print(await import_entries(db, entries(), apply=True, publish_reviewed=args.publish_reviewed))
    finally:
        client.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('directory', type=Path)
    cli.add_argument('--apply', action='store_true')
    cli.add_argument('--publish-reviewed', action='store_true')
    asyncio.run(run(cli.parse_args()))
