import re
from fastapi import APIRouter, Depends, Query, HTTPException
from pymongo.errors import ExecutionTimeout
from auth import get_current_user
from database import get_db
from services.dictionary_data import search_key, lesson_entry

router = APIRouter(prefix='/api/dictionary', tags=['dictionary'])


@router.get('/search')
async def search_dictionary(q: str = Query('', max_length=200), language_id: str | None = Query(None, max_length=60),
                            limit: int = Query(20, ge=1, le=100), current_user=Depends(get_current_user)):
    term = search_key(q)
    if not term:
        return []
    db = get_db()
    prefix = {'$regex': '^' + re.escape(term)}
    match = {'status': 'published', '$or': [{'native_key': prefix}, {'english_key': prefix}]}
    if language_id:
        match['language_id'] = language_id
    try:
        results = await db.dictionary_entries.find(match, {'_id': 0, 'native_key': 0, 'english_key': 0}).limit(limit).max_time_ms(2000).to_list(limit)
        pipeline = [
            {'$match': {'status': {'$nin': ['draft', 'rejected', 'pending_review']}}},
            {'$unwind': '$questions'},
            {'$match': {'questions.type': 'translate', '$or': [
                {f'questions.{field}': {'$regex': re.escape(q.strip()), '$options': 'i'}}
                for field in ('prompt', 'native_text', 'options.text')]}},
            {'$lookup': {'from': 'units', 'localField': 'unit_id', 'foreignField': 'id', 'as': 'unit'}},
            {'$unwind': '$unit'},
        ]
        if language_id:
            pipeline.append({'$match': {'unit.language_id': language_id}})
        pipeline.extend([
            {'$lookup': {'from': 'languages', 'localField': 'unit.language_id', 'foreignField': 'id', 'as': 'language'}},
            {'$unwind': '$language'}, {'$limit': 200},
            {'$project': {'_id': 0, 'id': 1, 'questions': 1, 'language': 1}},
        ])
        rows = await db.lessons.aggregate(pipeline, maxTimeMS=2000).to_list(200)
    except ExecutionTimeout:
        raise HTTPException(503, 'Dictionary search took too long. Try a longer word or choose a language.') from None
    seen = {(search_key(e['native']), search_key(e['english']), e['language_id']) for e in results}
    for row in rows:
        entry = lesson_entry(row['questions'], row, row['language'])
        if not entry or not any(term in search_key(entry[k]) for k in ('native', 'english')):
            continue
        key = (search_key(entry['native']), search_key(entry['english']), entry['language_id'])
        if key not in seen:
            results.append(entry)
            seen.add(key)
    return results[:limit]
