"""Validate drafts without connecting anywhere; --apply is an explicit owner action."""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.foundations import import_foundations


async def run(args):
    modules = json.loads(args.file.read_text(encoding='utf-8'))
    if not args.apply:
        print(await import_foundations(None, modules, publish_reviewed=args.publish_reviewed))
        return
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ['MONGODB_URI'], serverSelectionTimeoutMS=10000)
    try:
        print(await import_foundations(client[os.environ['DB_NAME']], modules, True, args.publish_reviewed))
    finally:
        client.close()


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('file', type=Path)
    cli.add_argument('--apply', action='store_true')
    cli.add_argument('--publish-reviewed', action='store_true')
    asyncio.run(run(cli.parse_args()))
