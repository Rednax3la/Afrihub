"""Foundations are separate from numbered units: no XP or entitlement migration."""
import re
from urllib.parse import urlsplit


def validate_foundation(module):
    required = ('id', 'language_id', 'title', 'stage', 'body', 'sources', 'status')
    if not all(module.get(key) for key in required):
        raise ValueError('Incomplete foundation module')
    if module['stage'] not in ('orthography', 'sounds', 'contrasts', 'listening'):
        raise ValueError('Invalid foundation stage')
    if not re.fullmatch(r'[a-z]+-foundation-[1-4]', module['id']):
        raise ValueError('Invalid stable foundation ID')
    if module['status'] not in ('draft', 'published'):
        raise ValueError('Invalid foundation status')
    if module['status'] == 'published':
        if not module.get('reviewed_by') or not module.get('reviewed_at'):
            raise ValueError('Publication requires linguistic review')
        if module['stage'] in ('sounds', 'contrasts', 'listening'):
            recordings = module.get('recordings', [])
            if not recordings or any(urlsplit(r.get('audio_url', '')).scheme != 'https'
                or not r.get('speaker_consent') or not r.get('reviewed_by') for r in recordings):
                raise ValueError('Pronunciation requires reviewed, consented tutor recordings')
    return module


async def import_foundations(db, modules, apply=False, publish_reviewed=False):
    for module in modules:
        validate_foundation(module)
        from services.dictionary_data import LANGUAGE_IDS
        if module['language_id'] not in LANGUAGE_IDS or not module['id'].startswith(module['language_id'] + '-foundation-'):
            raise ValueError('Foundation language does not match its stable ID')
        if module['status'] == 'published' and not publish_reviewed:
            raise ValueError('Use an explicit reviewed publication import')
    if apply:
        await db.foundations.create_index('id', unique=True)
        await db.foundations.create_index([('language_id', 1), ('status', 1), ('order', 1)])
        for module in modules:
            # Never overwrite reviewed live content by rerunning the draft seed.
            update = {'$set': module} if module['status'] == 'published' else {'$setOnInsert': module}
            await db.foundations.update_one({'id': module['id']}, update, upsert=True)
    return {'validated': len(modules), 'applied': apply}
