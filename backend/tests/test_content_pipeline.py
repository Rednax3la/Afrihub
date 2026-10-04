import ast
import copy
import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from mongomock_motor import AsyncMongoMockClient
from httpx import AsyncClient, ASGITransport
import database
from auth import get_current_user
from main import app
from services.dictionary_data import normalize_wiktionary, import_entries, search_key, lesson_entry, LANGUAGE_IDS
from services.foundations import import_foundations

ROOT = Path(__file__).resolve().parents[2]


def candidate():
    source = json.loads((ROOT / 'content/dictionary/sources.json').read_text())[0]
    return normalize_wiktionary({'word': 'mĩtĩ', 'lang_code': 'ki', 'lang': 'Kikuyu', 'pos': 'noun',
        'senses': [{'glosses': ['trees'], 'tags': ['plural']}, {'glosses': ['wood']}],
        'examples': [{'text': 'must not copy'}]}, source, 'mock-checksum')


def test_languages_exactly_match_generator_not_old_seed():
    module = ast.parse((ROOT / 'backend/generate_content.py').read_text(encoding='utf-8'))
    langs = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == 'LANGUAGES' for t in n.targets))
    assert len(langs) == 14
    assert set(langs) == LANGUAGE_IDS
    assert {x['id']: x['code'] for x in json.loads((ROOT / 'content/languages.json').read_text())} == {k:v['code'] for k,v in langs.items()}


def test_unicode_senses_and_attribution_preserved():
    entries = candidate()
    assert len(entries) == 2 and entries[0]['_id'] != entries[1]['_id']
    assert entries[0]['native'] == 'mĩtĩ' and entries[0]['english'] == 'trees'
    assert search_key('MI\u0303TI\u0303') == 'mĩtĩ'
    assert search_key('miti') != search_key('mĩtĩ')
    assert entries[0]['tags'] == ['plural']
    assert entries[0]['source']['license'] == 'CC-BY-SA-4.0'
    assert 'examples' not in entries[0] and 'audio_url' not in entries[0]
    assert entries[0]['status'] == 'draft'


async def test_dictionary_import_dry_run_idempotency_and_review_gate():
    entries = candidate()
    assert (await import_entries(None, entries))['validated'] == 2
    db = AsyncMongoMockClient().test_import
    assert (await import_entries(db, entries, True))['inserted'] == 2
    assert (await import_entries(db, entries, True))['existing'] == 2
    reviewed = copy.deepcopy(entries[0]); reviewed.update(status='published', review_status='reviewed')
    with pytest.raises(ValueError):
        await import_entries(db, [reviewed], True)
    reviewed.update(reviewed_by='test-reviewer', reviewed_at='2026-10-03')
    await import_entries(db, [reviewed], True, True)
    await import_entries(db, entries, True)
    assert (await db.dictionary_entries.find_one({'_id': reviewed['_id']}))['status'] == 'published'


def test_quiz_translation_comes_from_correct_option_not_pronunciation():
    q = {'type':'translate', 'prompt':'Habari', 'native_text':'ha-BA-ri', 'correct_answer_id':'a',
         'options':[{'id':'a','text':'News'}, {'id':'b','text':'Tree'}]}
    assert lesson_entry(q, {'id':'lesson'}, {'id':'swahili','name':'Swahili'})['english'] == 'News'


async def test_foundations_import_leaves_existing_units_progress_and_entitlements_unchanged(monkeypatch):
    db = AsyncMongoMockClient().test_foundations
    monkeypatch.setattr(database, 'db', db)
    modules = json.loads((ROOT / 'content/foundations/drafts.json').read_text(encoding='utf-8'))
    assert len(modules) == 56
    assert (await import_foundations(None, modules))['applied'] is False
    await db.units.insert_many([{'id':'free', 'language_id':'kikuyu','order':3}, {'id':'premium','language_id':'kikuyu','order':4}])
    await db.lessons.insert_many([{'id':'free-lesson','unit_id':'free','status':'published'}, {'id':'paid-lesson','unit_id':'premium','status':'published'}])
    await db.progress.insert_one({'user_id':'test', 'lesson_id':'free-lesson','completed':True})
    before = await db.units.find().to_list(None)
    await import_foundations(db, modules, True)
    await import_foundations(db, modules, True)
    assert await db.foundations.count_documents({}) == 56
    assert await db.units.find().to_list(None) == before
    assert (await db.progress.find_one({'user_id':'test'}))['completed']
    app.dependency_overrides[get_current_user] = lambda: {'_id':'test', 'role':'student'}
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='https://test') as client:
            data = (await client.get('/api/languages/kikuyu/foundations')).json()
            assert data['modules'] == [] and data['status'] == 'awaiting_tutor_review'
            units = (await client.get('/api/languages/kikuyu/units')).json()
            assert [u['locked'] for u in units] == [False, True]
            assert units[1]['lessons'] == []
            assert (await client.get('/api/lessons/paid-lesson')).status_code == 403
            text = copy.deepcopy(modules[0]); text.update(status='published', reviewed_by='tutor', reviewed_at='2026-10-03')
            await import_foundations(db, [text], True, True)
            assert len((await client.get('/api/languages/kikuyu/foundations')).json()['modules']) == 1
    finally:
        app.dependency_overrides.clear()


async def test_sound_publication_requires_human_recording_consent():
    module = json.loads((ROOT / 'content/foundations/drafts.json').read_text(encoding='utf-8'))[1]
    module.update(status='published', reviewed_by='tutor', reviewed_at='2026-10-03')
    with pytest.raises(ValueError, match='recordings'):
        await import_foundations(None, [module], publish_reviewed=True)


async def test_independent_dictionary_search_hides_drafts_and_keeps_diacritics(monkeypatch):
    db = AsyncMongoMockClient().test_dictionary
    monkeypatch.setattr(database, 'db', db)
    rows = candidate()
    await import_entries(db, rows, True)
    rows[0].update(status='published',review_status='reviewed',reviewed_by='tutor',reviewed_at='2026-10-03')
    await import_entries(db, [rows[0]], True, True)
    app.dependency_overrides[get_current_user] = lambda: {'_id':'test'}
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url='https://test') as client:
            found = (await client.get('/api/dictionary/search', params={'q':'MĨ','language_id':'kikuyu'})).json()
            assert len(found) == 1 and found[0]['english'] == 'trees' and found[0]['source']['license']
            for q in ['wood', 'mi', '.*']:
                assert (await client.get('/api/dictionary/search',params={'q':q})).json() == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize('app_env', [None, 'production'])
async def test_unconfigured_payment_availability_does_not_claim_purchase_ready(monkeypatch, app_env):
    from routes.payments import payment_availability
    for name in ('MPESA_CONSUMER_KEY','STRIPE_SECRET_KEY','APP_ENV'):
        monkeypatch.delenv(name, raising=False)
    if app_env: monkeypatch.setenv('APP_ENV', app_env)
    monkeypatch.setenv('MPESA_ENVIRONMENT','sandbox')
    monkeypatch.setenv('GOOGLE_PAY_ENVIRONMENT','TEST')
    response = await payment_availability()
    data = json.loads(response.body)
    assert not data['mpesa'] and not data['google_pay']
    assert response.headers['cache-control'] == 'no-store'


def test_collection_cache_resume_deduplication_and_robots(monkeypatch, tmp_path):
    from scripts.collect_dictionary import collect
    from unittest.mock import Mock
    source = json.loads((ROOT / 'content/dictionary/sources.json').read_text())[0]
    row = {'word':'mĩtĩ', 'lang_code':'ki', 'lang':'Kikuyu', 'pos':'noun', 'senses':[{'glosses':['trees']}]}
    payload = ((json.dumps(row) + '\n') * 2).encode()
    class Response:
        status_code = 200
        text = 'User-agent: *\nDisallow: /dictionary/search/\n'
        def raise_for_status(self): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def iter_content(self, size): yield payload
    session = Mock(headers={})
    session.get.return_value = Response()
    monkeypatch.setattr('scripts.collect_dictionary.time.sleep', lambda seconds: None)
    first = collect([source], tmp_path, session)
    assert first['kikuyu']['entries'] == 1
    assert session.get.call_count == 2
    second = collect([source], tmp_path, session)
    assert second == first
    assert session.get.call_count == 3  # only robots rechecked, no repeated source download
    blocked = dict(source, download_url='https://kaikki.org/dictionary/search/blocked')
    with pytest.raises(ValueError, match='robots'):
        collect([blocked], tmp_path, session)
