"""Unicode-preserving dictionary normalization; no database or network at import."""
import hashlib
import json
import unicodedata
from urllib.parse import quote, urlsplit

# Canonical IDs from generate_content.LANGUAGES; checked against the manifest in tests.
LANGUAGE_IDS = frozenset(['kikuyu', 'swahili', 'yoruba', 'zulu', 'amharic', 'luo', 'kalenjin', 'kamba', 'meru', 'luhya', 'igbo', 'hausa', 'shona', 'twi'])


def search_key(value):
    return unicodedata.normalize('NFC', value).casefold().strip()


def normalize_wiktionary(row, source, checksum):
    if row.get('lang_code') not in source['language_codes']:
        return []
    native = row.get('word')
    if not isinstance(native, str) or not native.strip() or len(native) > 300:
        return []
    entries = []
    for sense in row.get('senses', []):
        glosses = sense.get('glosses', [])
        if not glosses or not all(isinstance(g, str) and 0 < len(g) <= 2000 for g in glosses):
            continue
        tags = sorted(set(row.get('tags', []) + sense.get('tags', [])))
        entry = {
            'language_id': source['language_id'], 'language_name': source['language_name'],
            'native': native, 'english': '; '.join(glosses), 'glosses': glosses,
            'part_of_speech': row.get('pos', ''), 'tags': tags,
            'dialect': source.get('dialect', 'unspecified'),
            'review_status': 'unreviewed', 'status': 'draft', 'origin': 'dictionary',
            'source': {'id': source['id'], 'url': 'https://en.wiktionary.org/wiki/' + quote(native, safe='') + '#' + quote(row.get('lang', ''), safe=''),
                       'publisher': 'English Wiktionary contributors via Kaikki/Wiktextract',
                       'license': 'CC-BY-SA-4.0', 'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
                       'download_url': source['download_url'], 'sha256': checksum,
                       'changes': 'Selected headword, English glosses, POS and tags; normalized search keys; no examples or media.'},
        }
        identity = [source['id'], search_key(native), glosses, entry['part_of_speech'], tags, entry['dialect']]
        entry['_id'] = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        entry['native_key'], entry['english_key'] = search_key(native), search_key(entry['english'])
        entries.append(entry)
    return entries


def lesson_entry(question, lesson, language):
    if question.get('type') != 'translate' or not question.get('prompt'):
        return None
    options = question.get('options') or []
    correct = next((o.get('text') for o in options if o.get('id') == question.get('correct_answer_id')), None)
    # Quiz native_text is pronunciation; flashcard native_text is English.
    english = correct if options else question.get('native_text', '')
    if not english:
        return None
    return {'native': question['prompt'], 'english': english, 'language_id': language['id'],
            'language_name': language['name'], 'pronunciation': question.get('pronunciation', ''),
            'audio_url': question.get('audio_url'), 'origin': 'lesson', 'lesson_id': lesson['id'],
            'review_status': 'lesson_content', 'source': {'publisher': 'Vernaculearn lesson content'}}


async def dictionary_indexes(db):
    for field in ('native_key', 'english_key'):
        await db.dictionary_entries.create_index([('status', 1), (field, 1)])
        await db.dictionary_entries.create_index([('language_id', 1), ('status', 1), (field, 1)])


async def import_entries(db, entries, apply=False, publish_reviewed=False):
    counts = {'validated': 0, 'inserted': 0, 'existing': 0}
    for entry in entries:
        if not entry.get('_id') or not entry.get('native') or not entry.get('english') or not entry.get('source', {}).get('license'):
            raise ValueError('Entry lacks validated text or provenance')
        if entry.get('language_id') not in LANGUAGE_IDS or entry.get('status') not in ('draft', 'published'):
            raise ValueError('Invalid dictionary language or publication status')
        if any(urlsplit(entry['source'].get(key, '')).scheme != 'https' for key in ('url', 'license_url')):
            raise ValueError('Source and licence URLs must be HTTPS')
        if entry['status'] == 'published' and (not publish_reviewed or entry.get('review_status') != 'reviewed'
                or not entry.get('reviewed_by') or not entry.get('reviewed_at')):
            raise ValueError('Publication requires an explicit reviewed import and reviewer metadata')
        entry = {**entry, 'native_key': search_key(entry['native']), 'english_key': search_key(entry['english'])}
        counts['validated'] += 1
        if apply:
            update = {'$set': {k: v for k, v in entry.items() if k != '_id'}} if entry['status'] == 'published' else {'$setOnInsert': entry}
            result = await db.dictionary_entries.update_one({'_id': entry['_id']}, update, upsert=True)
            counts['inserted' if result.upserted_id else 'existing'] += 1
    return counts
